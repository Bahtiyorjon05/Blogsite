from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def highlight_search(text, search_term):
    """
    Highlight search terms in text with HTML markup
    """
    if not search_term or not text:
        return text
    
    # Escape HTML in search term to prevent XSS
    search_term = template.defaultfilters.escape(search_term)
    
    # Create case-insensitive regex pattern
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    
    # Replace matches with highlighted version
    highlighted = pattern.sub(
        f'<mark class="search-highlight">{search_term}</mark>', 
        str(text)
    )
    
    return mark_safe(highlighted)

@register.filter
def reading_time_text(minutes):
    """
    Convert reading time minutes to readable text
    """
    if minutes == 1:
        return "1 min read"
    else:
        return f"{minutes} mins read"

@register.filter 
def truncate_words_highlight(text, word_count):
    """
    Truncate text to word count and add ellipsis
    """
    words = str(text).split()
    if len(words) <= word_count:
        return text
    return ' '.join(words[:word_count]) + '...'