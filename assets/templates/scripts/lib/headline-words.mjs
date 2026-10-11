export function wrapHeadlineWords(root) {
  const visit = (node) => {
    for (const child of Array.from(node.childNodes)) {
      if (child.nodeType === 3) {
        const text = child.textContent;
        if (!text || !/\S/.test(text)) continue;
        const frag = child.ownerDocument.createDocumentFragment();
        for (const part of text.split(/(\s+)/)) {
          if (!part) continue;
          if (/^\s+$/.test(part)) frag.appendChild(child.ownerDocument.createTextNode(part));
          else {
            const span = child.ownerDocument.createElement("span");
            span.className = "w";
            span.textContent = part;
            frag.appendChild(span);
          }
        }
        child.parentNode.replaceChild(frag, child);
      } else if (child.nodeType === 1) visit(child);
    }
  };
  visit(root);
}
