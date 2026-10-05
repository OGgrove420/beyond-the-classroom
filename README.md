# Beyond The Classroom

Different Pace. Same Potential.

An adaptive online learning platform for learners who do not thrive in the
traditional classroom model — built by Conscious Mind Concepts (Pty) Ltd.

**The learner doesn't have to fit the system. The system adapts to the learner.**

## what this is (test build)

A working front-end + API for client demonstrations:

- landing page with the No Shame Learning philosophy
- learner profile builder (learning style, focus window, difficulty triggers)
- adaptive demo quiz: wrong answers never "fail" — they trigger
  "let's try that another way" with up to four alternative explanations
- parent dashboard (demo data) with weekly progress and insights
- tier pricing in ZAR (Discover free → Intensive R1 499/mo)

## stack

- static front-end: `public/` (vanilla js, no build step)
- api: `api/index.py` (vercel python runtime, in-memory demo state)
- content: `data/site.json` (single source for copy, tiers, subjects)

## run locally

Any static server for `public/` plus a python server for `/api/*` — or just
deploy to Vercel, which is the intended home:

```
vercel --prod
```

## status

Phase 1: online learning and academic support platform. Before marketing as a
formal school, South African educational status (registration, curriculum,
assessment and qualification pathways) must be confirmed.

All numbers shown are demo data.
