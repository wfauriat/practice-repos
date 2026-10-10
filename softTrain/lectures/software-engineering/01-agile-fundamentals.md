# Agile fundamentals

## Abstract

"Agile" was a reaction to a specific failure mode of 1990s enterprise software development. The canonical Agile is a four-line manifesto and twelve principles — modest, philosophical, concrete. The Agile most companies practise today is a brand around standups, story points, and Jira boards, which is largely orthogonal to the original idea.

## Motivation

You will spend a meaningful fraction of your career inside an "agile process." Knowing what the founders meant — and the failure modes that prompted them to write it — is the difference between *participating thoughtfully* and *cargo-culting through standup*. It also lets you tell, in a job interview or a planning meeting, the difference between teams that have actually internalised the values and teams that have copied the rituals.

The deeper motivation: most software is built under uncertainty about *what* should be built and *how long* it'll take. Methodologies that pretend otherwise — by fixing scope, schedule, and resources upfront — fail in predictable ways: scope grows, deadlines slip, and the team is blamed. Agile's contribution was to take that uncertainty as a primary fact and design around it.

## Core concepts

### The Manifesto (2001)

Seventeen developers met at a ski resort in Snowbird, Utah, and wrote four lines:

> Individuals and interactions over processes and tools  
> Working software over comprehensive documentation  
> Customer collaboration over contract negotiation  
> Responding to change over following a plan
>
> *That is, while there is value in the items on the right, we value the items on the left more.*

The often-forgotten coda matters. The right-hand items aren't *bad*; they're not *primary*. A team without documentation is not Agile. A team that refuses to write a contract is not Agile. The Manifesto names a *priority order* under conflict, not a list of forbidden activities.

### The Twelve Principles

These flesh out the Manifesto. Worth reading in full, but five are foundational:

1. **Welcome changing requirements, even late.** The competitive advantage of being able to change direction *during* development.
2. **Deliver working software frequently.** Weeks, not months.
3. **Working software is the primary measure of progress.** Not lines of code, story points, or burndown charts.
4. **At regular intervals, the team reflects on how to become more effective.** The retrospective is non-negotiable.
5. **Simplicity — the art of maximising the amount of work not done — is essential.** This is the principle most people miss. Doing less is a discipline.

### What Agile is not

- **Not Scrum.** Scrum is one *implementation* of Agile, with specific ceremonies (standup, sprint planning, retro, review). Many teams equate the two; this is a category error. You can be Agile without sprints, story points, or a Scrum Master.
- **Not "no documentation."** The Manifesto values working software *over* comprehensive documentation, not *instead of* it. Architecture decision records, API contracts, runbooks — these matter.
- **Not "no planning."** It values responding to change over following *a plan* (a fixed plan). It does not say "don't plan." Agile teams plan constantly; they just don't pretend the first plan is final.
- **Not "shippable in two weeks."** Sprints are a Scrum thing. The principle is *frequent* delivery, not specifically biweekly.

### The schools that diverged

After ~2005, Agile fragmented into schools with different shapes:

- **Scrum** — sprints, ceremonies, roles (Product Owner, Scrum Master, Team). The most-practised, most-misapplied. Works best when the *Product Owner* role is filled by someone with real authority and presence.
- **Extreme Programming (XP)** — pair programming, TDD, continuous integration, refactoring, simple design. Shaped engineering practice more than process. Most working developers do XP-flavoured engineering even if their process is "Scrum."
- **Kanban** — pull-based, work-in-progress limits, no fixed-length iterations. Better for ops/maintenance teams where work is stochastic.
- **Shape Up** (Basecamp, 2019) — six-week cycles, two-week cooldowns, fixed time + variable scope, "appetite" instead of estimates. A direct rejection of Scrum's biweekly sprint structure.
- **Lean** (Mary and Tom Poppendieck, drawing on Toyota) — flow, pull, eliminating waste. Influenced everything that came after.

Each school is internally coherent and addresses different failure modes. The mistake is mixing rituals from one school with values from another and getting frankenmethod incoherence.

## Tradeoffs / counterpoints

### Scrum theatre is real

Most "Agile" teams in 2026 do something like: *standup at 9:30 (which is a status report, not a daily plan), 2-week sprints (which slip), story points (which are estimates pretending not to be), and a retrospective (which surfaces the same problems quarter after quarter without resolution).* Each ritual exists; none of them produce the *behaviours* the Manifesto describes.

Diagnostic: when scope changes mid-sprint, what happens? If the answer is "we tell them to wait for next sprint," the team is doing Scrum, not Agile. The *first principle* (welcome changing requirements) is being actively violated by the very process meant to enable it.

### Story-point inflation

Story points were intended as a *team-relative*, *non-comparable* unit ("this is twice as much as that, in our judgement"). In practice they get aggregated, compared across teams, used for performance reviews, and inflated. The system corrupts itself.

The deeper issue is that estimates are usually wrong by 2-3x in either direction, and aggregating thousands of bad estimates produces precise nonsense. Several schools (Shape Up, no-estimates) abandon them entirely.

### "Working software" is not always the right primary measure

For teams shipping consumer features, "working software in users' hands" is a great measure. For teams building infrastructure, security, or research-heavy products, it's a poor proxy. A six-month rewrite of a database engine isn't "not working" because it doesn't ship weekly — but applying the principle naively will lead to "MVP rewrites" that ship and then get rewritten again because the architecture was wrong.

The principle is best read as: **whatever you build, find a feedback loop that's faster than "we'll know in 18 months."** That might be unit tests, simulations, customer interviews, or beta releases.

### Agile against engineering culture

XP packed Agile with engineering practices (TDD, pair programming, refactoring). Scrum, as it spread to non-engineering management consultancies, lost most of these. The result: a lot of teams that "do Agile" with terrible engineering practices — no tests, no refactoring discipline, no CI. Process-without-engineering is a recipe for "agile" delivery of accumulating debt.

If you join a team that does Scrum, ask about their engineering practices, not their ceremonies. Two-week sprints with no test coverage is just two-week waterfall.

### When NOT to be Agile

- **Heavy regulatory contexts** (medical devices, aerospace) require staged validation that's hard to do in 2-week cycles. Hybrid models exist but are non-trivial.
- **Hardware** — where iteration cycles are weeks to months and "working software frequently" doesn't apply directly.
- **Single-author, well-specified problems** — sometimes the spec really is clear and you just need to implement it. Adding ceremony to a clear problem is a tax.

## Further reading

1. **Agilemanifesto.org** — read the manifesto and twelve principles. Takes 5 minutes. Most "Agile" practitioners haven't.
2. **Mary & Tom Poppendieck — *Lean Software Development* (2003)** — the Lean roots. Especially the seven wastes chapter.
3. **Ron Jeffries — *The Nature of Software Development*** — gentle, opinionated, deeply experienced. A short read.
4. **Basecamp — *Shape Up*** (free online, [basecamp.com/shapeup](https://basecamp.com/shapeup)) — read this if your only exposure to Agile is Scrum. Shape Up takes a different bet, well argued.
5. **Allen Holub — assorted talks** ("Why Scrum Is The Wrong Way to Build Software") — provocative but a useful counter-balance to Scrum-as-default.

## Discussion prompts

1. **Pick one of the four Manifesto values.** Describe a team you've seen (or worked on) that *claimed* to embody it but in practice didn't. What was the gap between the ritual and the value?
2. **The principle "simplicity — the art of maximising the amount of work not done" is widely under-practised.** Why? Where in your own work do you accumulate unnecessary complexity, and what would "doing less" look like concretely?
3. **Story points have well-known failure modes.** Could you design a planning process that avoids them and still gives leadership the predictability they want? What would you replace them with?
4. **Suppose you joined a team where every Scrum ritual is in place but the engineers don't write tests, don't pair, and ship buggy releases.** What's your first month's intervention? Where would you push, and what would you leave alone?
5. **The Manifesto is silent on architecture.** XP is opinionated about it ("simplest thing that could possibly work" + refactoring). Some Agile-adjacent thinkers (Robert Martin) layered Clean Architecture on top. Was the Manifesto's silence a strength or a weakness?
