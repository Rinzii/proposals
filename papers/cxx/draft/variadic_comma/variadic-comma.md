---
title: "Require the comma before C varargs"
document: DnnnnR0
status: progress
date: 2026-11-23
audience:
  - EWG
  - CWG
author:
  - name: Ian Pike
    email: <ianpike98cs@gmail.com>
  - name: Eczbek
    email: <eczbek.void@gmail.com>
  - name: Jan Schultke
    email: <janschultke@gmail.com>
  - name: James Touton
    email: <bekenn@gmail.com>
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

In C++26, `void f(int...);` is a deprecated spelling of `void f(int, ...);` ([[depr.ellipsis.comma]](https://wg21.link/depr.ellipsis.comma)). We propose requiring the comma in C++29 whenever C varargs follow a parameter list. The declaration without the comma would then be ill-formed, but the existing rule would still determine whether a trailing `...` denotes C varargs or a parameter pack.

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
Forward DnnnnR0 to CWG for inclusion in C++29.
:::

# Migration {#migration}

Some valid C++26 programs would become ill-formed because they use the deprecated spelling. For example, suppose an otherwise valid program declares `void f(int...);` at namespace scope. Under the proposed rule, a conforming implementation would have to issue at least one diagnostic message ([[intro.compliance.general]/2](https://wg21.link/intro.compliance.general#2)).

We can migrate such a declaration before switching to C++29 because the spelling with the comma is valid in every language mode ([@P1219R3], section 6). As Table 1 shows, the comma goes between the parameter list and the C varargs ellipsis, where C already requires it ([@P3176R1], section 2.1). Inserting it there preserves the C++ function type ([[dcl.fct]/3](https://wg21.link/dcl.fct#4)).

:::: {#migration-spellings}

| Deprecated in C++26                       | With the comma                              |
| ----------------------------------------- | ------------------------------------------- |
| `int print_log(const char* fmt...);`      | `int print_log(const char* fmt, ...);`      |
| `using F = void(int...);`                 | `using F = void(int, ...);`                 |
| `template<class... Ts> void g(Ts......);` | `template<class... Ts> void g(Ts..., ...);` |

: [`Table 1:`{=html} Deprecated spellings and the same declarations with the comma.]{#migration-spellings-caption}

::::

In the last row, the comma separates the pack expansion `Ts...` from the `...` for C varargs. The declaration `template<class... Ts> void g(Ts...);` has only the pack expansion and `void f(...);` has only C varargs. Neither needs a separator so both remain valid as written.

```{=latex}
\clearpage
```

# Wording {#wording}

Wording is relative to [@CPP-DRAFT].

## Functions [dcl.fct] {#wording-functions}

::: {#wording-pack-expansion .draftnote}

[[dcl.fct]/26](https://wg21.link/dcl.fct#27) determines whether a trailing `...` without a preceding comma belongs to the [abstract-declarator]{.grammar-term} or the [parameter-declaration-clause]{.grammar-term}. We keep the [parameter-declaration-list]{.grammar-term} `...` alternative in the grammar because the final branch of [[dcl.fct]/26](https://wg21.link/dcl.fct#27) still selects it. The proposed wording makes that form ill-formed.

The rule in [[dcl.fct]/26](https://wg21.link/dcl.fct#27) mentions template parameter packs and `auto`. There are other kinds of pack in [[temp.variadic]/5](https://wg21.link/temp.variadic#5), including function parameter packs, init-capture packs, and structured binding packs. To see how the rule treats a structured binding pack, suppose `v` in the example below has two elements, an `int` followed by a `double`.

```cpp
template<class...> struct Types {};

template<class T> void inspect(T x) {
  auto [...v] = x;
  using R = Types<decltype(v)(decltype(v)...)...>;
}
```

Under [[dcl.fct]/26](https://wg21.link/dcl.fct#27), the inner `...` denotes C varargs because `decltype(v)` neither names a template parameter pack nor contains `auto`. The outer `...` expands `v` ([[temp.variadic]/8](https://wg21.link/temp.variadic#8)). For the first element of `v`, both occurrences of `decltype(v)` give `int` so the first type in `R` is `int(int, ...)`.

Now suppose [[dcl.fct]/26](https://wg21.link/dcl.fct#27) also covered the other kinds of pack. The inner `...` would then expand `v` into the two parameter types, `int` and `double`. For the first type in `R`, the outer expansion would still supply `int` as the return type so the function type would be `int(int, double)`.

Whether [[dcl.fct]/26](https://wg21.link/dcl.fct#27) should cover those packs is a separate question. In either case, our proposal applies only to C varargs following a parameter list. It requires the comma there and preserves the current meaning of every other use of the ellipsis.

:::

Modify [[dcl.fct]/3](https://wg21.link/dcl.fct#4) as follows:

:::: {#wording-comma-requirement .wording}

[[3]{.pnum}](https://wg21.link/dcl.fct#4) [...]
[Where syntactically correct and where "`...`" is not part of an *abstract-declarator*, "`...`" is synonymous with "`, ...`". A *parameter-declaration-clause* of the form `$parameter-declaration-list$ ...`{.default} is deprecated ([depr.ellipsis.comma]).]{.rm}
[The form `$parameter-declaration-list$ ...`{.default} shall not be used for a *parameter-declaration-clause*.]{.add}
[...]

::::

```{=latex}
\clearpage
```

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

## Annex C (informative) Compatibility [diff] {#wording-compatibility}

Add a new entry to [[diff.cpp26.dcl]](https://wg21.link/diff.cpp26.dcl) before the [dcl.init] entry:

:::: {.wording}

::::: {.add}

[]{#wording-compatibility-entry}[**Affected subclause:** [dcl.fct]]{.add}

[**Change:** A comma is required between a *parameter-declaration-list* and a following ellipsis.]{.add}

[**Rationale:** Distinguish a vararg function from a function with a trailing function parameter pack.]{.add}

[**Effect on original feature:** A valid C++ 2026 program that omits this comma is ill-formed. Inserting the comma preserves the function type.]{.add}

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

