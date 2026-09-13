# Workflows

Reusable GitHub Actions workflows for my repositories. Everything here is public, because a public repository can only call a public workflow.

A repository calls one by naming it in a job and follows `main`, so a fix here reaches every caller without a pull request in each:

```yaml
jobs:
  title:
    uses: azohra/.github/.github/workflows/title.yml@main
```

`title.yml` checks that a pull request title is a Conventional Commit line. It reports as `title / Conventional PR title`, the check the fleet's rulesets require.
