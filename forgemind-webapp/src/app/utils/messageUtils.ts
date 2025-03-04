/**
 * Utility functions for message handling
 */

/**
 * Function to check if a message contains Python code for CAD
 */
export function containsPythonCADCode(message: string): boolean {
  // If the message is very short, it's unlikely to be code
  if (!message || message.length < 10) return false;

  // Check for Python code blocks that start with ```python or ```
  if (message.includes('```python') || message.match(/```\s*\n[\s\S]*?import\s+/) || message.match(/```\s*\n[\s\S]*?def\s+/)) {
    return true;
  }

  // Function and class definition detection
  if (message.match(/def\s+\w+\s*\([^)]*\)\s*:/) || message.match(/class\s+\w+\s*\([^)]*\)\s*:/)) {
    return true;
  }

  // Import statements
  if (message.match(/import\s+adsk/) || message.match(/from\s+adsk\s+import/) || 
      message.match(/import\s+math/) || message.match(/import\s+[a-zA-Z0-9_]+\s*,\s*[a-zA-Z0-9_]+/)) {
    return true;
  }
  
  // Python specific functions and syntax
  if (message.match(/adsk\.core\./) || message.match(/adsk\.fusion\./) || 
      message.match(/\.get\(\)/) || message.match(/\.add\(/) || 
      message.match(/\.create\(/)) {
    return true;
  }

  // Check for Python indentation patterns (line starts with spaces followed by specific patterns)
  const lines = message.split('\n');
  let pythonCodeLineCount = 0;
  
  for (const line of lines) {
    if (line.match(/^\s+(?:if|for|while|def|class|return|import|from|try|except)\b/) || 
        line.match(/^\s+[a-zA-Z0-9_]+\s*=/) ||
        line.match(/^\s+#/)) {
      pythonCodeLineCount++;
    }
  }

  // If we detect several Python-like indented lines, consider it code
  if (pythonCodeLineCount >= 3) {
    return true;
  }

  return false;
} 