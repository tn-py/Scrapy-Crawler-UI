import difflib
import requests
from parsel import Selector

def explain_selector(selector: str) -> str:
    """
    Explains a CSS selector in plain English.
    """
    explanation = f"Explaining selector: {selector}\n"
    
    # This is a very basic implementation.
    # It can be expanded to be more comprehensive.
    
    if selector.startswith("#"):
        explanation += f"Selects the element with the id '{selector[1:]}'."
    elif selector.startswith("."):
        explanation += f"Selects all elements with the class '{selector[1:]}'."
    elif "[" in selector and "]" in selector:
        parts = selector.split("[")
        tag = parts[0]
        attr_part = parts[1].replace("]", "")
        attr, value = attr_part.split("=")
        value = value.strip("'\"")
        if tag:
            explanation += f"Selects all '{tag}' elements "
        else:
            explanation += "Selects all elements "
        explanation += f"with the attribute '{attr}' equal to '{value}'."
    else:
        explanation += f"Selects all '<{selector}>' elements."
        
    return explanation

def repair_selector(url: str, selector: str) -> str:
    """
    Repairs a broken CSS selector.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        sel = Selector(text=content)
        
        if sel.css(selector).get():
            return "Selector is valid and finds elements."

        # If the user enters a class name without a dot, add it.
        repaired_selector = selector
        if not selector.startswith((".", "#", "[")) and " " not in selector:
            repaired_selector = f".{selector}"

        # Check if the repaired selector is now valid
        if sel.css(repaired_selector).get():
            return f"Selector is valid. Did you mean to use '{repaired_selector}'?"

        if repaired_selector.startswith("."):
            class_name = repaired_selector[1:]
            all_classes = sel.xpath('//@class').getall()
            all_classes = " ".join(all_classes).split()
            
            close_matches = difflib.get_close_matches(class_name, all_classes)
            if close_matches:
                return f"Selector did not find any elements. Did you mean '.{close_matches[0]}'?"
            else:
                return "Selector did not find any elements and no close matches were found."
        
        return "Selector repair for this type of selector is not implemented yet."

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"