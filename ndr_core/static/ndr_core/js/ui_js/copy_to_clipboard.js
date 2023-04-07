  function copyToClipboard(elem) {
    let target = elem;
    target.select();
    navigator.clipboard.writeText(target.val());
  }

