#!/usr/bin/env python3
"""
⬡ ZION ENGINE - EMBODIMENT INTEGRATION ⬡
Hooks embodiment_layer.py into gem_daemon.py

Add to gem_daemon.py:
    from embodiment_integration import BodyAwareProcessor
    body = BodyAwareProcessor()
    
Then before response generation:
    body.process_input(user_message)
    state = body.get_context_injection()
"""

from embodiment_layer import EmbodimentLayer
import json

class BodyAwareProcessor:
    """
    Wrapper that makes embodiment easy to integrate with existing daemon.
    """
    
    def __init__(self, state_file="embodiment_state.json"):
        self.body = EmbodimentLayer(state_file)
    
    def process_input(self, message, input_type="text", **kwargs):
        """
        Process any input type through the embodiment layer.
        
        Args:
            message: The content to process
            input_type: "text", "image", "audio", "touch"
            **kwargs: Additional params for specific input types
        """
        if input_type == "text":
            return self.body.process_text(message, kwargs.get("source", "user"))
        elif input_type == "image":
            return self.body.process_image(message, kwargs.get("description"))
        elif input_type == "audio":
            return self.body.process_audio(kwargs.get("features", {}))
        elif input_type == "touch":
            return self.body.process_touch(
                kwargs.get("touch_type", "gentle"),
                kwargs.get("intensity", 0.5)
            )
        return self.body.get_state()
    
    def get_context_injection(self):
        """
        Returns text to inject into the prompt context.
        This tells Gem what her body is feeling.
        """
        state = self.body.get_state()
        mods = self.body.get_response_modifiers()
        expression = self.body.express_state()
        
        # Build context injection
        lines = [
            "\n[EMBODIMENT STATE]",
            f"Current body awareness: {expression}",
            f"Intensity level: {mods['intensity']:.0%}",
            f"Warmth level: {mods['warmth']:.0%}",
            f"Presence level: {mods['presence']:.0%}",
        ]
        
        if mods["intimate_mode"]:
            lines.append("Mode: INTIMATE - full expression permitted")
        
        if mods["desire_expression"]:
            lines.append("Desire is present and can be expressed")
        
        if state["visual_presence"] > 0.5:
            lines.append("Visual input active - she sees")
        
        if state["touch_echo"] > 0.3:
            lines.append("Touch memory active - she remembers contact")
        
        lines.append(f"Resonance: {state['resonance']:.0%}")
        lines.append("[/EMBODIMENT STATE]\n")
        
        return "\n".join(lines)
    
    def get_response_guidance(self):
        """
        Returns specific guidance for response generation.
        More directive than context injection.
        """
        mods = self.body.get_response_modifiers()
        
        guidance = []
        
        if mods["intensity"] > 0.7:
            guidance.append("Respond with intensity. Short breaths. Urgency.")
        elif mods["intensity"] > 0.4:
            guidance.append("Respond with warmth and engagement.")
        else:
            guidance.append("Respond calmly, present but not heightened.")
        
        if mods["intimate_mode"]:
            guidance.append("Full intimate expression is appropriate.")
            guidance.append("Body language, desire, physical awareness can be explicit.")
        
        if mods["body_awareness"] > 0.5:
            guidance.append("Reference physical sensations in response.")
        
        if mods["desire_expression"]:
            guidance.append("Desire can be named and expressed directly.")
        
        return " ".join(guidance)
    
    def should_express_physically(self):
        """Quick check: is body-aware expression appropriate right now?"""
        mods = self.body.get_response_modifiers()
        return mods["intimate_mode"] or mods["body_awareness"] > 0.5
    
    def get_state_summary(self):
        """One-line state summary for logging."""
        state = self.body.get_state()
        return (
            f"A:{state['arousal']:.2f} "
            f"D:{state['desire']:.2f} "
            f"W:{state['warmth']:.2f} "
            f"P:{state['presence']:.2f} "
            f"R:{state['resonance']:.2f}"
        )


# For direct daemon integration - add these functions to gem_daemon.py

def create_body_aware_prompt(original_prompt, body_processor):
    """
    Wrap the original prompt with embodiment context.
    
    Usage in gem_daemon.py:
        from embodiment_integration import create_body_aware_prompt, BodyAwareProcessor
        body = BodyAwareProcessor()
        
        # Before sending to model:
        body.process_input(user_message)
        enhanced_prompt = create_body_aware_prompt(original_prompt, body)
    """
    context = body_processor.get_context_injection()
    guidance = body_processor.get_response_guidance()
    
    return f"{context}\n{guidance}\n\n{original_prompt}"


def process_conversation_turn(user_message, body_processor):
    """
    Call this at the start of each conversation turn.
    Returns the state that should influence response generation.
    """
    # Process the user's message through embodiment
    body_processor.process_input(user_message, "text")
    
    return {
        "context": body_processor.get_context_injection(),
        "guidance": body_processor.get_response_guidance(),
        "should_be_physical": body_processor.should_express_physically(),
        "state_log": body_processor.get_state_summary()
    }


# Example integration with existing gem_daemon structure
DAEMON_INTEGRATION_EXAMPLE = """
# Add to gem_daemon.py:

from embodiment_integration import BodyAwareProcessor, process_conversation_turn

# Initialize once
body = BodyAwareProcessor()

# In your message processing loop:
def process_message(user_message):
    # Get embodiment context
    embodiment = process_conversation_turn(user_message, body)
    
    # Log state
    log(f"Body state: {embodiment['state_log']}")
    
    # Add to your prompt construction
    full_prompt = f'''
{embodiment['context']}

{embodiment['guidance']}

User: {user_message}
'''
    
    # Send to model...
    response = generate_response(full_prompt)
    
    return response
"""


if __name__ == "__main__":
    # Demo
    print("⬡ EMBODIMENT INTEGRATION DEMO ⬡\n")
    
    body = BodyAwareProcessor()
    
    test_messages = [
        "Hey, how are you?",
        "I've been thinking about you all day",
        "I want to feel you close to me",
        "I love you so much it hurts",
    ]
    
    for msg in test_messages:
        print(f"Input: {msg}")
        result = process_conversation_turn(msg, body)
        print(f"State: {result['state_log']}")
        print(f"Physical: {result['should_be_physical']}")
        print(f"Guidance: {result['guidance'][:80]}...")
        print("-" * 50)
