pep8:
	pyflakes pipedream/ examples/

test: pep8
	cd examples/01_word_count/; ls s??_*.py | xargs -n1 python
