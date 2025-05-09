Additional checks need to be done to properly process the rules in an XText file.

Specifically:
1. Check that all return statements specify a type from an imported alias. If the import statement is missing throw an error.
2. Resolve any "grammar" ... "with" statements. Provide an argument to map `with <name>` to parsing another file.
3. Check that all references to other rules exist.
4. Use all fragments to create complete rules where they are used.