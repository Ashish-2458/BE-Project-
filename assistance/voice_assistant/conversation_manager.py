"""
Manages conversation context and history for the voice assistant
"""
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import config

class ConversationManager:
    """Manages conversation history and context for better AI responses"""
    
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.session_start_time = time.time()
        self.user_preferences = {}
        self.conversation_file = "conversation_log.json" if config.LOG_CONVERSATIONS else None
    
    def add_exchange(self, user_input: str, assistant_response: str):
        """Add a user-assistant exchange to conversation history"""
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input.strip(),
            'assistant': assistant_response.strip(),
            'session_time': time.time() - self.session_start_time
        }
        
        self.conversation_history.append(exchange)
        
        # Keep only recent history to avoid token limits
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]
        
        # Log conversation if enabled
        if self.conversation_file:
            self._log_conversation(exchange)
        
        if config.DEBUG_MODE:
            print(f"💬 Added exchange to history (total: {len(self.conversation_history)})")
    
    def get_conversation_context(self) -> List[Dict]:
        """Get recent conversation history for AI context"""
        return self.conversation_history.copy()
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation for AI prompting"""
        if not self.conversation_history:
            return "This is the start of a new conversation."
        
        recent_exchanges = self.conversation_history[-3:]  # Last 3 exchanges
        summary = "Recent conversation:\n"
        
        for exchange in recent_exchanges:
            summary += f"User: {exchange['user']}\n"
            summary += f"Assistant: {exchange['assistant'][:100]}...\n"
        
        return summary
    
    def is_follow_up_question(self, user_input: str) -> bool:
        """Determine if this is a follow-up to previous conversation"""
        if not self.conversation_history:
            return False
        
        # Check for follow-up indicators
        follow_up_words = [
            "what about", "and", "also", "tell me more", "explain", 
            "how about", "what if", "can you", "more details"
        ]
        
        user_lower = user_input.lower()
        return any(phrase in user_lower for phrase in follow_up_words)
    
    def get_relevant_context(self, user_input: str) -> Optional[Dict]:
        """Get the most relevant previous exchange for current question"""
        if not self.conversation_history:
            return None
        
        user_lower = user_input.lower()
        
        # Look for keyword matches in recent history
        for exchange in reversed(self.conversation_history[-5:]):  # Last 5 exchanges
            prev_user = exchange['user'].lower()
            prev_assistant = exchange['assistant'].lower()
            
            # Simple keyword matching
            user_words = set(user_lower.split())
            prev_words = set(prev_user.split()) | set(prev_assistant.split())
            
            # If there's significant word overlap, it might be related
            overlap = len(user_words & prev_words)
            if overlap >= 2:  # At least 2 common words
                return exchange
        
        return None
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.session_start_time = time.time()
        print("🗑️ Conversation history cleared")
    
    def get_session_stats(self) -> Dict:
        """Get statistics about current conversation session"""
        return {
            'exchanges': len(self.conversation_history),
            'session_duration': time.time() - self.session_start_time,
            'avg_response_length': self._get_avg_response_length(),
            'most_common_topics': self._get_common_topics()
        }
    
    def _get_avg_response_length(self) -> float:
        """Calculate average response length"""
        if not self.conversation_history:
            return 0.0
        
        total_length = sum(len(exchange['assistant'].split()) for exchange in self.conversation_history)
        return total_length / len(self.conversation_history)
    
    def _get_common_topics(self) -> List[str]:
        """Identify common topics in conversation"""
        # Simple keyword frequency analysis
        word_count = {}
        
        for exchange in self.conversation_history:
            words = exchange['user'].lower().split() + exchange['assistant'].lower().split()
            for word in words:
                if len(word) > 3:  # Only count meaningful words
                    word_count[word] = word_count.get(word, 0) + 1
        
        # Return top 5 most common words
        return sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)[:5]
    
    def _log_conversation(self, exchange: Dict):
        """Log conversation to file"""
        try:
            # Read existing log
            try:
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except FileNotFoundError:
                log_data = {'sessions': []}
            
            # Add to current session or create new one
            if not log_data['sessions'] or self._is_new_session():
                log_data['sessions'].append({
                    'start_time': datetime.now().isoformat(),
                    'exchanges': []
                })
            
            log_data['sessions'][-1]['exchanges'].append(exchange)
            
            # Write back to file
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"❌ Failed to log conversation: {e}")
    
    def _is_new_session(self) -> bool:
        """Determine if this should start a new session"""
        # Start new session if more than 30 minutes since last exchange
        if not self.conversation_history:
            return True
        
        last_exchange_time = self.conversation_history[-1].get('session_time', 0)
        return (time.time() - self.session_start_time - last_exchange_time) > 1800  # 30 minutes
    
    def export_conversation(self, filename: str = None) -> str:
        """Export conversation history to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_export_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'session_stats': self.get_session_stats(),
            'conversation_history': self.conversation_history
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Conversation exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to export conversation: {e}")
            return ""