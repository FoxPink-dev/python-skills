"""Ownership marker utilities for generated content."""

from typing import Optional, Tuple


# Standard ownership markers
BEGIN_MARKER = "<!-- BEGIN PYTHON-SKILLS MANAGED -->"
END_MARKER = "<!-- END PYTHON-SKILLS MANAGED -->"

# Format-specific markers
MARKERS = {
    "md": (BEGIN_MARKER, END_MARKER),
    "mdc": (BEGIN_MARKER, END_MARKER),
    "mdx": (BEGIN_MARKER, END_MARKER),
    "txt": (BEGIN_MARKER, END_MARKER),
    "yaml": ("# PYTHON-SKILLS MANAGED", "# END PYTHON-SKILLS MANAGED"),
    "yml": ("# PYTHON-SKILLS MANAGED", "# END PYTHON-SKILLS MANAGED"),
    "json": ("// PYTHON-SKILLS MANAGED", "// END PYTHON-SKILLS MANAGED"),
    "py": ("# PYTHON-SKILLS MANAGED", "# END PYTHON-SKILLS MANAGED"),
    "js": ("// PYTHON-SKILLS MANAGED", "// END PYTHON-SKILLS MANAGED"),
    "ts": ("// PYTHON-SKILLS MANAGED", "// END PYTHON-SKILLS MANAGED"),
}


def get_markers(file_path: str) -> tuple[str, str]:
    """Get ownership markers for a file type."""
    ext = file_path.split(".")[-1].lower() if "." in file_path else "md"
    return MARKERS.get(ext, (BEGIN_MARKER, END_MARKER))


def wrap_managed_content(content: str, file_path: str) -> str:
    """Wrap content with ownership markers."""
    begin, end = get_markers(file_path)
    return f"{begin}\n{content}\n{end}"


def extract_managed_region(content: str, file_path: str) -> Optional[str]:
    """Extract content between ownership markers."""
    begin, end = get_markers(file_path)
    
    start_idx = content.find(begin)
    if start_idx == -1:
        return None
    
    start_idx += len(begin)
    end_idx = content.find(end, start_idx)
    if end_idx == -1:
        return None
    
    return content[start_idx:end_idx]


def replace_managed_region(content: str, new_content: str, file_path: str) -> tuple[str, bool]:
    """
    Replace content between ownership markers.
    
    Returns:
        Tuple of (new_content, was_replaced)
    """
    begin, end = get_markers(file_path)
    
    start_idx = content.find(begin)
    if start_idx == -1:
        # No existing managed region - append at end
        if content.strip():
            new_content_wrapped = f"\n{wrap_managed_content(new_content, file_path)}"
            return content + new_content_wrapped, True
        return wrap_managed_content(new_content, file_path), True
    
    end_idx = content.find(end, start_idx)
    if end_idx == -1:
        # Malformed - no end marker
        return content, False
    
    # Replace region
    new_content_full = content[:start_idx] + wrap_managed_content(new_content, file_path) + content[end_idx + len(end):]
    return new_content_full, True


def remove_managed_region(content: str, file_path: str) -> tuple[str, bool]:
    """
    Remove the managed region from content.
    
    Returns:
        Tuple of (new_content, was_removed)
    """
    begin, end = get_markers(file_path)
    
    start_idx = content.find(begin)
    if start_idx == -1:
        return content, False
    
    end_idx = content.find(end, start_idx)
    if end_idx == -1:
        return content, False
    
    # Remove region including markers
    new_content = content[:start_idx] + content[end_idx + len(end):]
    return new_content, True


def has_managed_region(content: str, file_path: str) -> bool:
    """Check if content has a managed region."""
    begin, end = get_markers(file_path)
    start_idx = content.find(begin)
    if start_idx == -1:
        return False
    end_idx = content.find(end, start_idx)
    return end_idx != -1


def compute_region_hash(content: str, file_path: str) -> Optional[str]:
    """Compute hash of managed region content."""
    import hashlib
    region = extract_managed_region(content, file_path)
    if region is None:
        return None
    return hashlib.sha256(region.encode("utf-8")).hexdigest()


def is_managed_region_modified(content: str, file_path: str, expected_hash: str) -> bool:
    """Check if managed region has been modified by user."""
    current_hash = compute_region_hash(content, file_path)
    if current_hash is None:
        return True  # No region = modified/corrupted
    return current_hash != expected_hash


def find_managed_regions(content: str, file_path: str) -> list[tuple[int, int, str]]:
    """
    Find all managed regions in content.
    
    Returns list of (start_idx, end_idx, content) tuples.
    """
    begin, end = get_markers(file_path)
    regions = []
    
    search_start = 0
    while True:
        start_idx = content.find(begin, search_start)
        if start_idx == -1:
            break
        
        end_idx = content.find(end, start_idx + len(begin))
        if end_idx == -1:
            break
        
        region_content = content[start_idx + len(begin):end_idx]
        regions.append((start_idx, end_idx + len(end), region_content))
        search_start = end_idx + len(end)
    
    return regions