import sqlite3
import os
import hashlib
import time
import fnmatch # Added for pattern matching

class FilesystemIndexer:
    def __init__(self, db_path='filesystem.db', root_dir='.', exclude_dirs=None, exclude_patterns=None):
        self.db_path = db_path
        self.root_dir = os.path.abspath(root_dir)
        # Ensure exclude_dirs are absolute paths for consistent checking
        self.exclude_dirs = {os.path.abspath(d) for d in (exclude_dirs if exclude_dirs is not None else [])}
        self.exclude_patterns = exclude_patterns if exclude_patterns is not None else []
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Initializes the SQLite database and creates the files table if it doesn't exist."""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                is_dir INTEGER NOT NULL,
                size INTEGER,
                mod_time REAL,
                content_hash TEXT,
                last_scanned_time REAL,
                last_analyzed_time REAL DEFAULT 0
            )
        ''')
        self.conn.commit()

    def _calculate_file_hash(self, file_path, block_size=65536):
        """Calculates the SHA256 hash of a file's content."""
        if not os.path.isfile(file_path):
            return None
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    hasher.update(block)
            return hasher.hexdigest()
        except IOError:
            return None # Handle permission issues or files that disappear during hashing

    def _should_exclude(self, path):
        """Checks if a path should be excluded based on configured patterns and directories."""
        abs_path = os.path.abspath(path)

        # Check for directory exclusion
        for ed in self.exclude_dirs:
            if abs_path.startswith(ed): # Use startswith for directory trees
                return True

        # Check for pattern exclusion
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        return False

    def scan_filesystem(self):
        """Scans the filesystem from the root_dir, updates the database with new/modified/deleted files."""
        print(f"Scanning filesystem from: {self.root_dir}")
        current_files_on_disk = set()
        timestamp = time.time()
        cursor = self.conn.cursor()

        # Iterate through root_dir, handling each entry
        for entry in os.listdir(self.root_dir):
            full_path = os.path.join(self.root_dir, entry)
            if self._should_exclude(full_path):
                continue
            
            # Add to current_files_on_disk (all scanned paths)
            current_files_on_disk.add(full_path)

            # Handle files and directories differently
            if os.path.isdir(full_path):
                # Recursively walk subdirectories if not excluded
                for dirpath, dirnames, filenames in os.walk(full_path, topdown=True):
                    # Filter dirnames in-place for os.walk to skip excluded subdirs
                    dirnames[:] = [d for d in dirnames if not self._should_exclude(os.path.join(dirpath, d))]
                    
                    for dname in dirnames: # Add subdirectories that are being walked
                        sub_dir_path = os.path.join(dirpath, dname)
                        if not self._should_exclude(sub_dir_path):
                            current_files_on_disk.add(sub_dir_path)

                    for fname in filenames:
                        file_path = os.path.join(dirpath, fname)
                        if not self._should_exclude(file_path):
                            current_files_on_disk.add(file_path)
                            self._process_file(file_path, timestamp, cursor)
                self._process_directory(full_path, timestamp, cursor) # Process the top-level directory
            elif os.path.isfile(full_path):
                self._process_file(full_path, timestamp, cursor)

        # Identify and remove deleted files/directories from DB
        # This needs to be done carefully to only remove what was actually scanned.
        # A full scan ensures that anything not found is indeed deleted.
        cursor.execute("SELECT path FROM files WHERE path LIKE ?", (self.root_dir + '%',)) # Only paths within our root_dir
        all_db_paths_in_root = set(row[0] for row in cursor.fetchall())
        
        deleted_paths = all_db_paths_in_root - current_files_on_disk
        for deleted_path in deleted_paths:
            print(f"Detected deleted: {deleted_path}")
            cursor.execute("DELETE FROM files WHERE path = ?", (deleted_path,))
        
        self.conn.commit()
        print("Filesystem scan complete.")

    def _process_file(self, full_path, timestamp, cursor):
        """Helper to process individual file entries."""
        db_entry = None
        try:
            cursor.execute("SELECT id, size, mod_time, content_hash FROM files WHERE path = ?", (full_path,))
            db_entry = cursor.fetchone()
        except sqlite3.OperationalError:
            # Handle cases where the table might not exist or other DB issues
            pass

        try:
            current_size = os.path.getsize(full_path)
            current_mod_time = os.path.getmtime(full_path)
        except (FileNotFoundError, PermissionError):
            # File might have been deleted right after os.walk or during permission checks
            print(f"Warning: Could not access file {full_path}. Skipping.")
            return

        current_hash = None 

        if db_entry:
            # Check for modifications
            if db_entry[1] != current_size or db_entry[2] != current_mod_time:
                current_hash = self._calculate_file_hash(full_path)
                if current_hash != db_entry[3]: # Only update if hash actually changed
                    cursor.execute("UPDATE files SET size = ?, mod_time = ?, content_hash = ?, last_scanned_time = ?, last_analyzed_time = 0 WHERE id = ?",
                                   (current_size, current_mod_time, current_hash, timestamp, db_entry[0]))
                else: # Size/mod_time changed but hash didn't (e.g., metadata-only change or hash collision unlikely)
                    cursor.execute("UPDATE files SET size = ?, mod_time = ?, last_scanned_time = ? WHERE id = ?",
                                   (current_size, current_mod_time, timestamp, db_entry[0]))
            else: # File not modified, just update scan time
                cursor.execute("UPDATE files SET last_scanned_time = ? WHERE id = ?", (timestamp, db_entry[0]))
        else:
            # New file
            current_hash = self._calculate_file_hash(full_path)
            cursor.execute("INSERT INTO files (path, name, is_dir, size, mod_time, content_hash, last_scanned_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (full_path, os.path.basename(full_path), 0, current_size, current_mod_time, current_hash, timestamp))

    def _process_directory(self, full_path, timestamp, cursor):
        """Helper to process individual directory entries."""
        db_entry = None
        try:
            cursor.execute("SELECT id, mod_time FROM files WHERE path = ?", (full_path,))
            db_entry = cursor.fetchone()
        except sqlite3.OperationalError:
            pass # Table might not exist yet

        try:
            current_mod_time = os.path.getmtime(full_path)
        except (FileNotFoundError, PermissionError):
            print(f"Warning: Could not access directory {full_path}. Skipping.")
            return

        if db_entry:
            if db_entry[1] != current_mod_time:
                cursor.execute("UPDATE files SET mod_time = ?, last_scanned_time = ? WHERE id = ?", 
                               (current_mod_time, timestamp, db_entry[0]))
            else:
                cursor.execute("UPDATE files SET last_scanned_time = ? WHERE id = ?", (timestamp, db_entry[0]))
        else:
            cursor.execute("INSERT INTO files (path, name, is_dir, size, mod_time, last_scanned_time) VALUES (?, ?, ?, ?, ?, ?)",
                           (full_path, os.path.basename(full_path), 1, 0, current_mod_time, timestamp))

    def get_unanalyzed_files(self):
        """Returns a list of files that have been modified or are new and haven't been analyzed."""
        cursor = self.conn.cursor()
        # Ensure we only get files (is_dir = 0) that are actual files on disk
        # and haven't been analyzed recently enough (mod_time > last_analyzed_time)
        cursor.execute("SELECT path FROM files WHERE is_dir = 0 AND (last_analyzed_time = 0 OR last_analyzed_time < mod_time)")
        return [row[0] for row in cursor.fetchall()]

    def mark_as_analyzed(self, file_path):
        """Marks a file as analyzed by updating its last_analyzed_time."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE files SET last_analyzed_time = ? WHERE path = ?", (time.time(), file_path))
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

if __name__ == '__main__':
    # Example Usage:
    # Exclude common directories that change often or are large
    exclude_dirs = [
        './.git', './node_modules', './.venv', './__pycache__',
        './.cache', './.npm', './.nvm', './.vscode', './.config',
        './snap', './.local', './.thunderbird', './.mozilla',
        '/home/robert-moore/.gemini/memory' # Exclude my internal memory database
    ]
    # Exclude specific file patterns (e.g., temporary files, compiled files)
    exclude_patterns = ['*.log', '*.tmp', '*.pyc', '*.sqlite3', '*.db', '*.DS_Store']

    # IMPORTANT: Set root_dir to the actual home directory
    indexer = FilesystemIndexer(
        db_path='filesystem.db', 
        root_dir='/home/robert-moore', 
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns
    )
    
    # Perform a scan
    indexer.scan_filesystem()

    # Get files that need analysis
    unanalyzed_files = indexer.get_unanalyzed_files()
    if unanalyzed_files:
        print(f"\nFound {len(unanalyzed_files)} files to analyze:")
        for f in unanalyzed_files:
            print(f"  - {f}")
            # In a real scenario, you would call your content analysis engine here
            # For demonstration, we just mark it as analyzed
            # indexer.mark_as_analyzed(f)
    else:
        print("\nNo unanalyzed files found.")

    indexer.close()
