# pile
Rust based parsing and query for SysML V2 textual notation.

## Contributing
General architecture:
A Lark (Python) grammar is written to parse the SysML XText (Java) grammar and then generate a LALRPOP (Rust) grammar and associated Rust code, which is then compiled and bound to surrounding languages through FFI and WASM. Confused enough yet? No? Then lets go.

Development is highly encouraged to be done in the devcontainer to keep all environments stable. 