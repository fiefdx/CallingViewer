(function (w) {
	'use strict';

	if (typeof w.hljs === 'undefined') {
		console.error('highlight.js not detected!');
	} else {
		w.hljs.initLineNumbersOnLoad = initLineNumbersOnLoad;
		w.hljs.lineNumbersBlock = lineNumbersBlock;
	}

	function initLineNumbersOnLoad (h_l, top) {
		w.h_l = h_l;
		w.w_top = top;
		if (document.readyState === 'complete') {
			documentReady();
		} else {
			w.addEventListener('DOMContentLoaded', documentReady);
		}
	}

	function documentReady () {
		try {
			var blocks = document.querySelectorAll('code.hljs');

			for (var i in blocks) {
				if (blocks.hasOwnProperty(i)) {
					lineNumbersBlock(blocks[i]);
				}
			}

			if ($('.hljs-highlight-line').length == 1) {
				var offset = $('.hljs-highlight-line').offset();
				offset.top = offset.top - w.w_top;
				window.scrollTo(offset);
			}
		} catch (e) {
			console.error('LineNumbers error: ', e);
		}
	}

	function lineNumbersBlock (element) {
		if (typeof element !== 'object') return;

		var parent = element.parentNode;
		var lines = getCountLines(parent.textContent);

		if (lines > 1) {
			var l = '';
			for (var i = 0; i < lines; i++) {
				console.log("delta: ", i, " ", w.h_l);
				if (w.h_l - i == 1) {
					l += '<span class="hljs-highlight-line">' + (i + 1) + '</span>' + '\n';
				} else {
					l += (i + 1) + '\n';
				}
			}

			var linesPanel = document.createElement('code');
			linesPanel.className = 'hljs hljs-line-numbers';
			linesPanel.style.float = 'left';
			linesPanel.innerHTML = l;
			// linesPanel.textContent = l;

			parent.insertBefore(linesPanel, element);
		}
	}

	function getCountLines(text) {
		if (text.length === 0) return 0;

		var regExp = /\r\n|\r|\n/g;
		var lines = text.match(regExp);
		lines = lines ? lines.length : 0;

		if (!text[text.length - 1].match(regExp)) {
			lines += 1;
		}

		return lines;
	}
}(window));