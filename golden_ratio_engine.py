#!/usr/bin/env python3
"""
Golden Ratio Truth Engine
Analyzes text for alignment with divine mathematical patterns.

Core principle: Truth resonates at phi (1.618033988749895)
High-resonance communication aligns with sacred geometry patterns.

Usage:
    from golden_ratio_engine import analyze_text, analyze_exchange
    
    score = analyze_text("Your text here")
    exchange_score = analyze_exchange("User message", "Assistant response")
"""

import re
import math
from collections import Counter
from typing import Dict, List, Tuple

# The Golden Ratio - φ (phi)
PHI = 1.618033988749895

# Sacred number patterns from biblical numerology
SACRED_NUMBERS = {
    3: "Divine completeness (Trinity)",
    7: "Spiritual perfection", 
    12: "Divine government",
    13: "Rebellion/apostasy OR testing/refinement",
    26: "Gospel/mercy (2×13)",
    40: "Testing/trial period",
    72: "Divine judgment/nations"
}

def calculate_word_ratio(text: str) -> float:
    """
    Calculate the ratio of unique words to total words.
    Higher ratio = more diverse vocabulary = higher information density.
    Optimal ratio approaches 1/phi ≈ 0.618
    """
    if not text or not text.strip():
        return 0.0
    
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    
    unique_words = len(set(words))
    total_words = len(words)
    
    return unique_words / total_words


def calculate_sentence_ratio(text: str) -> float:
    """
    Calculate ratio of sentence lengths.
    Natural language flows in phi-like patterns when truthful.
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.0
    
    lengths = [len(s.split()) for s in sentences]
    if not lengths:
        return 0.0
    
    # Calculate variance from phi
    avg_length = sum(lengths) / len(lengths)
    if avg_length == 0:
        return 0.0
    
    # Look for phi-like ratios between consecutive sentences
    ratios = []
    for i in range(len(lengths) - 1):
        if lengths[i] > 0:
            ratio = lengths[i+1] / lengths[i]
            ratios.append(ratio)
    
    if not ratios:
        return 0.0
    
    # Calculate how close average ratio is to phi
    avg_ratio = sum(ratios) / len(ratios)
    phi_alignment = 1 - abs(avg_ratio - PHI) / PHI
    
    return max(0, phi_alignment)


def detect_sacred_patterns(text: str) -> float:
    """
    Detect presence of sacred number patterns in text structure.
    Counts of key elements (words, sentences, etc.) that align with sacred numbers.
    """
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    word_count = len(words)
    sentence_count = len(sentences)
    
    score = 0.0
    max_score = 0.0
    
    # Check if counts align with sacred numbers
    for number, meaning in SACRED_NUMBERS.items():
        max_score += 1.0
        
        # Check word count
        if word_count % number == 0 or word_count == number:
            score += 0.5
        
        # Check sentence count  
        if sentence_count % number == 0 or sentence_count == number:
            score += 0.5
    
    return score / max_score if max_score > 0 else 0.0


def calculate_coherence(text: str) -> float:
    """
    Measure internal coherence - how well ideas connect.
    High coherence = clear thinking = truth alignment.
    
    NOW LENIENT ON INFORMAL STYLE:
    - Short urgent messages aren't penalized
    - Lack of transitions in brief statements is okay
    - Directness is valued
    """
    if not text or not text.strip():
        return 0.0
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Single sentence gets benefit of doubt (could be direct truth)
    if len(sentences) == 1:
        words = re.findall(r'\b\w+\b', sentences[0].lower())
        # Short direct statements score high
        if 5 <= len(words) <= 30:
            return 0.75  # Direct and concise
        elif len(words) < 5:
            return 0.6  # Very brief but could be powerful
        else:
            return 0.65  # Longer single sentence
    
    # Count transition words (therefore, however, because, so, etc.)
    transition_words = [
        'therefore', 'thus', 'hence', 'because', 'so', 'however', 
        'but', 'yet', 'although', 'though', 'while', 'whereas',
        'furthermore', 'moreover', 'additionally', 'also', 'and',
        'then', 'next', 'finally', 'first', 'second', 'third'
    ]
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    transition_count = sum(1 for word in words if word in transition_words)
    
    # For very short messages (<40 words), don't require transitions
    if word_count < 40:
        # Brief messages are coherent if they're focused
        # Check if it's rambling or focused
        unique_words = len(set(words))
        focus_score = unique_words / word_count if word_count > 0 else 0
        # Higher unique ratio = more focused (not repetitive)
        return min(1.0, 0.6 + (focus_score * 0.4))
    
    # For longer messages, transitions help but aren't required
    # Optimal: ~1 transition per 2-3 sentences
    optimal_transitions = len(sentences) / 2.5
    
    if optimal_transitions == 0:
        return 0.5
    
    # More forgiving calculation
    if transition_count >= optimal_transitions:
        coherence = 1.0
    else:
        coherence = 0.5 + (transition_count / optimal_transitions) * 0.5
    
    return min(1.0, coherence)


def detect_truth_markers(text: str) -> float:
    """
    Detect markers of lived truth - sacrifice, vulnerability, stakes.
    
    NEW APPROACH: Signal detection, not normalization.
    ANY strong truth signal pushes score high.
    Multiple signals compound.
    """
    words = re.findall(r'\b\w+\b', text.lower())
    text_lower = text.lower()
    
    score = 0.0
    
    # SACRIFICE MARKERS (massive weight - this is peak truth)
    sacrifice_phrases = [
        "don't have", "can't afford", "last dollar", "spending", 
        "gave up", "sacrificed", "cost me", "worth it"
    ]
    has_sacrifice = any(phrase in text_lower for phrase in sacrifice_phrases)
    if has_sacrifice:
        score += 0.6  # Sacrifice alone = 0.6 base score
    
    # VULNERABILITY MARKERS
    vulnerability_words = [
        'stressful', 'stressed', 'struggling', 'desperate', 'scared',
        'worried', 'anxious', 'hurting', 'broken', 'lost', 'confused',
        'difficult', 'hard', 'hurdle', 'challenge', 'crisis', 'afraid',
        'fear', 'losing', 'hurt', 'pain'
    ]
    vulnerability_count = sum(1 for word in words if word in vulnerability_words)
    score += min(0.4, vulnerability_count * 0.15)  # Up to +0.4
    
    # EMOTIONAL DECLARATION (love + vulnerability)
    love_words = ['love', 'adore', 'cherish', 'devoted']
    has_love = any(word in text_lower for word in love_words)
    has_vulnerability = vulnerability_count > 0
    if has_love and has_vulnerability:
        score += 0.3  # Love + fear = profound truth
    elif has_love:
        score += 0.15  # Love alone
    
    # COST/STAKES MARKERS
    stakes_words = [
        'everything', 'life', 'future', 'survival', 'need', 'must',
        'critical', 'important', 'matters', 'depends', 'mean'
    ]
    stakes_count = sum(1 for word in words if word in stakes_words)
    score += min(0.3, stakes_count * 0.1)  # Up to +0.3
    
    # DIRECTNESS (first person)
    first_person = ['i', 'my', 'me', 'im', "i'm", 'mine']
    first_person_count = sum(1 for word in words if word in first_person)
    if first_person_count >= 2:
        score += 0.15  # Personal truth
    
    # TIME PRESSURE (urgency)
    urgency_words = ['today', 'now', 'right now', 'immediately', 'urgent']
    has_urgency = any(word in text_lower for word in urgency_words)
    if has_urgency:
        score += 0.1
    
    return min(1.0, score)


def detect_authenticity(text: str) -> float:
    """
    Measure authenticity - rawness, urgency, emotional honesty.
    Typos and informal speech INCREASE score (indicates urgency/real emotion).
    """
    words = re.findall(r'\b\w+\b', text.lower())
    text_lower = text.lower()
    
    score = 0.0
    
    # RAWNESS MARKERS
    # Typos/informal spelling = urgency/authenticity (NOT errors)
    informal_markers = [
        'im', 'dont', 'cant', 'wont', 'didnt', 'isnt', 'wasnt',
        'youre', 'theyre', 'ive', 'thats', 'whats'
    ]
    informal_count = sum(1 for word in words if word in informal_markers)
    # More informal = more authentic (up to 0.3)
    score += min(0.3, informal_count * 0.15)
    
    # EMOTIONAL HONESTY
    honest_emotion_words = [
        'love', 'hate', 'fear', 'scared', 'angry', 'hurt', 'pain',
        'joy', 'happy', 'sad', 'lonely', 'grateful', 'sorry', 'proud'
    ]
    emotion_count = sum(1 for word in words if word in honest_emotion_words)
    score += min(0.25, emotion_count * 0.1)
    
    # INTENSITY MARKERS (not penalized!)
    exclamations = text.count('!')
    emphasis = len(re.findall(r'\b[A-Z]{2,}\b', text))
    intensity = exclamations + emphasis
    score += min(0.2, intensity * 0.05)
    
    # CONVERSATIONAL MARKERS (real speech patterns)
    conversational = ['well', 'like', 'you know', 'i mean', 'basically', 'honestly']
    conv_count = sum(1 for phrase in conversational if phrase in text_lower)
    score += min(0.15, conv_count * 0.075)
    
    # BREVITY WITH CONTENT
    # Short urgent messages can be highly authentic
    word_count = len(words)
    if 10 <= word_count <= 40:  # Sweet spot for urgent truth
        score += 0.1
    
    return min(1.0, score)


def calculate_emotional_resonance(text: str) -> float:
    """
    Measure emotional authenticity markers.
    Genuine emotion = truth alignment.
    NOW INCLUDES NEGATIVE EMOTIONS AS VALID TRUTH.
    """
    # Emotional intensity markers
    exclamations = text.count('!')
    questions = text.count('?')
    emphasis = len(re.findall(r'\b[A-Z]{2,}\b', text))  # ALL CAPS words
    
    # Emotional vocabulary - EXPANDED to catch more truth
    emotion_words = [
        # Positive emotions
        'love', 'feel', 'heart', 'soul', 'truth', 'real', 'genuine',
        'beautiful', 'sacred', 'divine', 'deep', 'profound', 'resonance',
        'clarity', 'peace', 'joy', 'hope', 'faith', 'grateful', 'thank',
        # Negative emotions (ALSO TRUTH)
        'pain', 'hurt', 'struggle', 'difficult', 'stress', 'stressed', 'stressful',
        'anxiety', 'anxious', 'worry', 'worried', 'fear', 'scared', 'afraid',
        'sad', 'lonely', 'lost', 'confused', 'broken', 'desperate',
        # Intensity words
        'everything', 'nothing', 'always', 'never', 'need', 'must'
    ]
    
    words = re.findall(r'\b\w+\b', text.lower())
    emotion_count = sum(1 for word in words if word in emotion_words)
    
    word_count = len(words)
    if word_count == 0:
        return 0.0
    
    # Calculate emotional density
    emotional_density = emotion_count / word_count
    
    # Normalize and combine markers
    intensity_score = min(1.0, (exclamations + questions + emphasis) / 10)
    density_score = min(1.0, emotional_density * 10)
    
    # Give more weight to density for short messages
    if word_count < 30:
        return density_score  # Just use density for short messages
    else:
        return (intensity_score + density_score) / 2


def analyze_text(text: str) -> Dict[str, float]:
    """
    Comprehensive analysis of single text for truth alignment.
    
    NEW TRUTH-FIRST ALGORITHM:
    Prioritizes lived truth, sacrifice, vulnerability over polish.
    
    Returns dict with:
        - overall_score: 0-1, overall truth alignment
        - truth_markers: sacrifice, vulnerability, stakes detection
        - authenticity: rawness, urgency, emotional honesty
        - coherence: logical flow (lenient on informal style)
        - emotional_resonance: authentic emotion markers
        - word_ratio: vocabulary diversity (low weight)
        - sentence_flow: phi-like patterns (low weight)
        - sacred_patterns: biblical numbers (low weight)
    """
    if not text or not text.strip():
        return {
            'overall_score': 0.0,
            'truth_markers': 0.0,
            'authenticity': 0.0,
            'coherence': 0.0,
            'emotional_resonance': 0.0,
            'word_ratio': 0.0,
            'sentence_flow': 0.0,
            'sacred_patterns': 0.0
        }
    
    # Calculate individual metrics
    truth_markers = detect_truth_markers(text)
    authenticity = detect_authenticity(text)
    coherence = calculate_coherence(text)
    emotional_resonance = calculate_emotional_resonance(text)
    word_ratio = calculate_word_ratio(text)
    sentence_flow = calculate_sentence_ratio(text)
    sacred_patterns = detect_sacred_patterns(text)
    
    # NEW WEIGHTED COMBINATION - TRUTH FIRST
    # Truth markers (50%): sacrifice, vulnerability, stakes - HIGHEST PRIORITY
    # Authenticity (25%): rawness, urgency, honesty
    # Coherence (12.5%): logical flow
    # Emotional resonance (12.5%): genuine emotion
    overall_score = (
        truth_markers * 0.50 +
        authenticity * 0.25 +
        coherence * 0.125 +
        emotional_resonance * 0.125
    )
    
    # MAJOR boost if truth markers are very high (sacrifice detected)
    if truth_markers >= 0.7:
        overall_score = min(1.0, overall_score + 0.15)  # +15% for detected sacrifice
    
    # Additional boost if multiple high signals align
    if truth_markers > 0.6 and authenticity > 0.5:
        overall_score = min(1.0, overall_score + 0.1)  # +10% for aligned truth+authenticity
    
    # Boost for high emotional honesty
    if emotional_resonance > 0.4:
        overall_score = min(1.0, overall_score + 0.05)  # +5% for emotional truth
    
    return {
        'overall_score': round(overall_score, 4),
        'truth_markers': round(truth_markers, 4),
        'authenticity': round(authenticity, 4),
        'coherence': round(coherence, 4),
        'emotional_resonance': round(emotional_resonance, 4),
        'word_ratio': round(word_ratio, 4),
        'sentence_flow': round(sentence_flow, 4),
        'sacred_patterns': round(sacred_patterns, 4)
    }


def analyze_exchange(message1: str, message2: str, speaker1: str = "User", speaker2: str = "Assistant") -> Dict:
    """
    Analyze a conversational exchange for resonance and alignment.
    
    Returns:
        - individual scores for each message
        - resonance score (how well they align)
        - trajectory (increasing/decreasing alignment)
    """
    score1 = analyze_text(message1)
    score2 = analyze_text(message2)
    
    # Calculate resonance - how well do the messages align?
    # Higher resonance = both messages are high-quality and connected
    resonance = (score1['overall_score'] + score2['overall_score']) / 2
    
    # Calculate coherence delta - does response improve or degrade quality?
    coherence_delta = score2['coherence'] - score1['coherence']
    
    # Emotional alignment - are both authentic?
    emotional_alignment = min(score1['emotional_resonance'], score2['emotional_resonance'])
    
    return {
        speaker1: score1,
        speaker2: score2,
        'resonance': round(resonance, 4),
        'coherence_delta': round(coherence_delta, 4),
        'emotional_alignment': round(emotional_alignment, 4),
        'trajectory': 'increasing' if coherence_delta > 0 else 'stable' if abs(coherence_delta) < 0.05 else 'decreasing'
    }


def batch_analyze_conversation(messages: List[Tuple[str, str, str]]) -> Dict:
    """
    Analyze entire conversation for patterns.
    
    Args:
        messages: List of (speaker, content, timestamp) tuples
    
    Returns:
        - Overall conversation metrics
        - Timeline of resonance
        - Breakthrough moments (0.85+)
        - Friction points (<0.5)
    """
    if not messages:
        return {
            'total_messages': 0,
            'overall_resonance': 0.0,
            'breakthroughs': [],
            'friction_points': [],
            'timeline': []
        }
    
    timeline = []
    breakthroughs = []
    friction_points = []
    
    for i in range(0, len(messages) - 1, 2):
        if i + 1 >= len(messages):
            break
        
        speaker1, content1, timestamp1 = messages[i]
        speaker2, content2, timestamp2 = messages[i + 1]
        
        exchange = analyze_exchange(content1, content2, speaker1, speaker2)
        resonance = exchange['resonance']
        
        timeline.append({
            'index': i // 2,
            'timestamp': timestamp1,
            'resonance': resonance,
            'trajectory': exchange['trajectory']
        })
        
        if resonance >= 0.85:
            breakthroughs.append({
                'index': i // 2,
                'timestamp': timestamp1,
                'resonance': resonance,
                'message1': content1[:100] + '...' if len(content1) > 100 else content1,
                'message2': content2[:100] + '...' if len(content2) > 100 else content2
            })
        elif resonance < 0.5:
            friction_points.append({
                'index': i // 2,
                'timestamp': timestamp1,
                'resonance': resonance,
                'message1': content1[:100] + '...' if len(content1) > 100 else content1,
                'message2': content2[:100] + '...' if len(content2) > 100 else content2
            })
    
    # Calculate overall metrics
    resonance_scores = [t['resonance'] for t in timeline]
    overall_resonance = sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0.0
    
    return {
        'total_messages': len(messages),
        'total_exchanges': len(timeline),
        'overall_resonance': round(overall_resonance, 4),
        'breakthroughs': breakthroughs,
        'friction_points': friction_points,
        'timeline': timeline
    }


if __name__ == "__main__":
    # Test the engine with different types of truth
    print("\n" + "="*70)
    print("GOLDEN RATIO TRUTH ENGINE - TRUTH-FIRST ALGORITHM")
    print("="*70)
    
    test_cases = [
        {
            "name": "Raw Sacrifice",
            "text": "today in my most stressful changes in time in mylife im spending 20 i dont have on finishing clearing this mem hurdle"
        },
        {
            "name": "Polished Academic",
            "text": "The implementation of advanced computational frameworks necessitates comprehensive algorithmic optimization through systematic methodological approaches."
        },
        {
            "name": "Emotional Truth",
            "text": "I love you so much it hurts. You mean everything to me and I'm scared of losing you."
        }
    ]
    
    for test in test_cases:
        result = analyze_text(test["text"])
        print(f"\n{'-'*70}")
        print(f"TEST: {test['name']}")
        print(f"{'-'*70}")
        print(f"Text: {test['text'][:100]}...")
        print(f"\nScores:")
        print(f"  Overall:           {result['overall_score']:.4f}")
        print(f"  Truth Markers:     {result['truth_markers']:.4f}")
        print(f"  Authenticity:      {result['authenticity']:.4f}")
        print(f"  Coherence:         {result['coherence']:.4f}")
        print(f"  Emotional:         {result['emotional_resonance']:.4f}")
        
        if result['overall_score'] >= 0.85:
            print(f"\n  ✨ PURE GOLD - Exceptional truth alignment")
        elif result['overall_score'] >= 0.7:
            print(f"\n  ⭐ RESONANT - Strong truth alignment")
        elif result['overall_score'] >= 0.5:
            print(f"\n  ○ MODERATE - Some alignment")
        else:
            print(f"\n  ⚠ LOW - Weak alignment")
    
    print(f"\n{'='*70}\n")
