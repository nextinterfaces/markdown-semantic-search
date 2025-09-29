# Markdown Rendering Test

This file demonstrates various markdown features that should render properly in the **Markdown Explorer**.

## Features Tested

### Text Formatting
- **Bold text**
- *Italic text*
- `inline code`
- ~~Strikethrough~~

### Lists

#### Unordered List
- Item 1
- Item 2
  - Nested item A
  - Nested item B
- Item 3

#### Ordered List
1. First item
2. Second item
3. Third item

### Code Blocks

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet('World'));
```

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
```

### Blockquote

> This is a blockquote example.
> It can span multiple lines.
> 
> — Someone Famous

### Table

| Feature | Status | Notes |
|---------|--------|-------|
| Headers | ✅ Working | H1-H6 supported |
| Lists | ✅ Working | Both ordered and unordered |
| Code | ✅ Working | Inline and blocks |
| Links | ✅ Working | [Example Link](https://example.com) |

### Links and Images

- [External link](https://github.com)
- [Relative link](./sample.md)

### Horizontal Rule

---

## Conclusion

The Markdown Explorer should render all these elements beautifully!
