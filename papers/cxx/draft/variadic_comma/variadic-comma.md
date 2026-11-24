---
title: "Require the comma before C varargs"
document: D4494R0
status: progress
date: 2026-11-23
audience:
  - EWG
  - CWG
author:
  - name: Ian Pike
    email: <ianpike98cs@gmail.com>
  - name: Jan Schultke
    email: <janschultke@gmail.com>
intent: Forward to CWG for C++29
references:
  - id: "CPP-DRAFT"
    citation-label: "N5054"
    title: "N5054: Working Draft, Programming Languages - C++"
    URL: "https://wg21.link/N5054"
  - id: "N3096"
    citation-label: "N3096"
    title: "Programming languages - C"
    URL: "https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3096.pdf"
    issued:
      literal: "1 April 2023"
  - id: "P1219R3"
    citation-label: "P1219R3"
    title: "Homogeneous variadic function parameters"
    URL: "https://wg21.link/p1219r3"
    author:
      - literal: "Ian Pike"
      - literal: "Eczbek"
      - literal: "Jan Schultke"
      - literal: "James Touton"
    issued:
      literal: "22 October 2026"
  - id: "P3176R1"
    citation-label: "P3176R1"
    title: "The Oxford variadic comma"
    URL: "https://wg21.link/p3176r1"
    author:
      - literal: "Jan Schultke"
    issued:
      literal: "22 November 2024"
---

# Abstract {.unnumbered .unlisted}

In C++26, `void f(int...);` is a deprecated spelling of `void f(int, ...);` ([[depr.ellipsis.comma]](https://wg21.link/depr.ellipsis.comma)). We propose requiring the comma in C++29 whenever C varargs follow a parameter list. A `...` that follows a parameter without a comma could then only be part of that parameter's declarator so the declaration without the comma would be ill-formed.

```{=latex}
\clearpage
```

# EWG direction {#direction}

In Búzios, EWG encouraged us to address the comma in a separate paper. Removing the deprecated spelling would let EWG consider using `int...` for an unnamed pack of `int` parameters, as proposed in [@P1219R3].

Requiring the comma would also make C++ and C23 agree on which spellings they accept for C varargs ([@N3096], 6.7.6). C has never allowed the comma to be omitted between a parameter list and the C varargs ellipsis ([@P3176R1], section 2.1).

::: {.recorded-poll label="Recorded EWG poll" source="https://github.com/cplusplus/papers/issues/297#issuecomment-7049311768" result="Consensus."}

P1219R3: Homogeneous variadic function parameters. EWG Is ok with making a missing-comma before a C varargs ill-formed in C++29

| SF  |  F  |  N  |  A  | SA  |
| :-: | :-: | :-: | :-: | :-: |
|  9  | 13  |  2  |  3  |  0  |

:::

::: {.proposed-poll label="Proposed EWG poll"}
Forward D4494R0 to CWG for inclusion in C++29.
:::

# Migration {#migration}

Some valid C++26 programs would become ill-formed because they use the deprecated spelling. For example, suppose an otherwise valid program declares `void f(int...);` at namespace scope. Under the proposed wording, a conforming implementation would have to issue at least one diagnostic message ([[intro.compliance.general]/2](https://wg21.link/intro.compliance.general#2)).

We can migrate such a declaration before switching to C++29 because the spelling with the comma is valid in every language mode ([@P1219R3], section 6). As Table 1 shows, the comma goes between the parameter list and the C varargs ellipsis. Inserting it there preserves the C++ function type ([[dcl.fct]/3](https://wg21.link/dcl.fct#4)).

:::: {#migration-spellings}

| Deprecated in C++26                       | With the comma                              |
| ----------------------------------------- | ------------------------------------------- |
| `int print_log(const char* fmt...);`      | `int print_log(const char* fmt, ...);`      |
| `using F = void(int...);`                 | `using F = void(int, ...);`                 |
| `template<class... Ts> void g(Ts......);` | `template<class... Ts> void g(Ts..., ...);` |

: [`Table 1:`{=html} Deprecated spellings and the same declarations with the comma.]{#migration-spellings-caption}

::::

In the last row, the comma separates the pack expansion `Ts...` from the `...` for C varargs. The declaration `template<class... Ts> void g(Ts...);`{.nobreak} has only the pack expansion and `void f(...);` has only C varargs. Neither needs a separator so both remain valid as written.

There is also a case where a declaration would stay well-formed but change meaning. It requires an unnamed last parameter whose type names a pack other than a template parameter pack, such as `decltype(v)` for a structured binding pack `v`. The [drafting note](#wording-pack-expansion) in the wording shows an example. Inserting the comma also preserves the C++26 meaning in that case.

```{=latex}
\clearpage
```

# Wording {#wording}

Wording is relative to [@CPP-DRAFT].

## Functions [dcl.fct] {#wording-functions}

::: {#wording-pack-expansion .draftnote}

Today a `...` that follows a parameter without a comma is either C varargs or part of that parameter's declarator. [[dcl.fct]/26](https://wg21.link/dcl.fct#27) is the rule that chooses between them. For example, it makes the `...` in `Ts...` part of the declarator when `Ts` is a template parameter pack.

We remove the [parameter-declaration-list]{.grammar-term} `...` alternative because it is the one that gives the C varargs meaning. Only the declarator meaning is left after that so the rule has nothing to choose between anymore. Therefore, we also remove the rule and its footnote.

The deprecated spellings below become ill-formed without a new rule.

```cpp
void f(int...);      // ill-formed: declares a pack but int names no pack
void f(int x...);    // ill-formed: no longer matches the grammar
void g(auto......);  // ill-formed: no longer matches the grammar
```

In the first declaration, `int...` now declares a function parameter pack. A function parameter pack is a pack expansion ([[dcl.fct]/25](https://wg21.link/dcl.fct#26)) and a pack expansion has to name an unexpanded pack ([[temp.variadic]/8](https://wg21.link/temp.variadic#8)). As `int` names no pack, the declaration is ill-formed for the same reason that `void f(int... x);` is ill-formed today.

There is also a spelling that stays well-formed but changes meaning. As written, [[dcl.fct]/26](https://wg21.link/dcl.fct#27) chooses the declarator meaning only if the parameter's type names an unexpanded template parameter pack or contains `auto`. Otherwise it chooses C varargs even if the type names a pack of another kind ([[temp.variadic]/5](https://wg21.link/temp.variadic#5)). For example, suppose that `v` in the code below is a structured binding pack whose elements are an `int` followed by a `double`.

```cpp
template<class...> struct Types {};

template<class T> void inspect(T x) {
  auto [...v] = x;
  using R = Types<decltype(v)(decltype(v)...)...>;
  // [dcl.fct]/26 as written: Types<int(int, ...), double(double, ...)>
  // proposed wording:        Types<int(int, double), double(int, double)>
}
```

Under [[dcl.fct]/26](https://wg21.link/dcl.fct#27) as written, the inner `...` is C varargs and only the outer `...` expands `v`. With the proposed wording, the inner `...` is part of the declarator so it expands `v` as well. Writing `decltype(v)(decltype(v), ...)`{.nobreak} with the comma gives the first result with either wording.

:::

```{=latex}
\clearpage
```

Modify [[dcl.fct]/1](https://wg21.link/dcl.fct#2) and [[dcl.fct]/3](https://wg21.link/dcl.fct#4) as follows and remove [[dcl.fct]/26](https://wg21.link/dcl.fct#27) with its footnote:

:::: {#wording-comma-requirement .wording}

[[1]{.pnum}](https://wg21.link/dcl.fct#2) [...]

```diff
  @*parameter-declaration-clause*@:
      ...
      @*parameter-declaration-list~opt~*@
      @*parameter-declaration-list*@ , ...
-     @*parameter-declaration-list*@ ...
```

[...]

[[3]{.pnum}](https://wg21.link/dcl.fct#4) [...]
[Where syntactically correct and where "`...`" is not part of an *abstract-declarator*, "`...`" is synonymous with "`, ...`". A *parameter-declaration-clause* of the form `$parameter-declaration-list$ ...`{.default} is deprecated ([depr.ellipsis.comma]).]{.rm}
[...]

[[26]{.pnum}](https://wg21.link/dcl.fct#27) [There is a syntactic ambiguity when an ellipsis occurs at the end of a *parameter-declaration-clause* without a preceding comma. In this case, the ellipsis is parsed as part of the *abstract-declarator* if the type of the parameter either names a template parameter pack that has not been expanded or contains `auto`; otherwise, it is parsed as part of the *parameter-declaration-clause*.]{.rm}

[[69)]{.pnum}](https://wg21.link/dcl.fct#footnote-69) [One can explicitly disambiguate the parse either by introducing a comma (so the ellipsis will be parsed as part of the *parameter-declaration-clause*) or by introducing a name for the parameter (so the ellipsis will be parsed as part of the *declarator-id*).]{.rm}

::::

## Annex D (normative) Compatibility features [depr] {#wording-deprecation}

Remove [[depr.ellipsis.comma]](https://wg21.link/depr.ellipsis.comma):

:::: {#wording-removed-ellipsis-clause .wording}

::::: {.rm}

[[D.5]{.pnum}](https://wg21.link/depr.ellipsis.comma)
[**Non-comma-separated ellipsis parameters [depr.ellipsis.comma]**]{.rm}

[A *parameter-declaration-clause* of the form `$parameter-declaration-list$ ...`{.default} is deprecated ([dcl.fct]).]{.rm}

:::::: {.example num=1}

```cpp
void f(int...);         // deprecated
void g(auto...);        // OK, declares a function parameter pack
void h(auto......);     // deprecated
```

::::::

:::::

::::

```{=latex}
\clearpage
```

## Annex C (informative) Compatibility [diff] {#wording-compatibility}

Add a new entry to [[diff.cpp26.dcl]](https://wg21.link/diff.cpp26.dcl) before the [dcl.init] entry:

:::: {.wording}

::::: {.add}

[]{#wording-compatibility-entry}[**Affected subclause:** [dcl.fct]]{.add}

[**Change:** A comma is required between a *parameter-declaration-list* and a following ellipsis.]{.add}

[**Rationale:** Distinguish a vararg function from a function with a trailing function parameter pack.]{.add}

[**Effect on original feature:** A valid C++ 2026 program that omits this comma is ill-formed, unless the ellipsis can be parsed as part of the *abstract-declarator* of the preceding *parameter-declaration* and the type of that parameter names a pack that has not been expanded. In that case the *parameter-declaration* declares a function parameter pack and the parameter-type-list no longer has an ellipsis. Inserting the comma preserves the function type.]{.add}

:::::: {.example num=1}

```cpp
template<class... Ts> void a(Ts...);   // OK, declares a function parameter pack
void b(auto...);                       // OK, declares a function parameter pack
void c(int, ...);                      // OK, declares a vararg function
void d(...);                           // OK, declares a vararg function
void e(int...);                        // ill-formed; previously well-formed
void f(int x...);                      // ill-formed; previously well-formed
void g(auto......);                    // ill-formed; previously well-formed
void h(auto..., ...);                  // OK, declares a vararg function
```

::::::

:::::

::::

# Acknowledgments {#acknowledgments}

Thanks to Eczbek and James Touton for their work on [@P1219R3], which this paper grew out of. Their insights and opinions were invaluable to its success.

