# Development Lessons Learned Diary

## Network Intelligence Packet Inspector (NIPI) Project

### Lesson #1: File Dependency Management
**Date:** June 10, 2025  
**Context:** NIPI Template Color Consistency Updates

**Lesson Learned:** Always check for file references throughout entire project when editing files - grep for filename patterns to find all references that need updating to prevent broken dependencies

**Details:**
- When updating template files and CSS classes, changes in one file can affect multiple other files
- Template inheritance systems require consistent updates across parent and child templates
- Color scheme changes need to be propagated through all related templates and CSS blocks

**Best Practice Going Forward:**
```bash
# Before making changes to any file, search for all references
grep -r "filename_pattern" /project/directory/
grep -r "class_name" /project/directory/
grep -r "function_name" /project/directory/

# For template changes, check for:
grep -r "block_name" templates/
grep -r "css_class" templates/ static/
grep -r "template_file.html" src/
```

**Impact:** This practice prevents broken dependencies, ensures consistent theming across applications, and reduces debugging time when making project-wide changes.

---

*Continue adding lessons learned as development progresses...*