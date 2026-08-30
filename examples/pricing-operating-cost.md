# Pricing and Operating-Cost Example

This hand-written illustration shows intended behavior for vendor recommendations. It is not a measured model comparison or verified current pricing; see [evaluations](../evals/README.md) for executed tests.

## Prompt

```text
I'm building a small SaaS with auth, Postgres, file uploads, and maybe background jobs later. Should I just use Supabase because it is free to start?
```

## Generic AI Answer

Likely recommendation:

- Use Supabase because it includes Postgres, auth, storage, edge functions, and a free tier.
- Deploy the frontend on Vercel.
- Upgrade later if you need more scale.

This can be directionally useful, but it is incomplete. "Free to start" does not answer whether the stack is cheap, predictable, or easy to exit once real users and storage arrive.

## Skill-Guided Answer

The skill should verify or explicitly mark unknown:

- base subscription or plan requirement
- per-project or per-organization costs
- database size, backups, replicas, connection pooling, and point-in-time recovery
- storage volume, bandwidth, transformations, CDN, and egress
- auth limits, monthly active users, MFA, SSO, organizations, and custom domains
- edge functions/background jobs and invocation limits
- logs, metrics, retention, and observability add-ons
- local development parity and self-hosting fallback
- migration path from managed Postgres/auth/storage if the service becomes expensive or limiting

## Better Recommendation Shape

```text
Supabase may still be the best choice if speed matters more than cost predictability and you want auth/storage/Postgres integrated quickly.

What you gain:
- fast build path
- managed Postgres/auth/storage
- fewer early infrastructure decisions

What you give up:
- less control over long-term cost shape
- vendor-specific auth/storage assumptions
- possible migration work if usage or pricing no longer fits

What becomes harder later:
- moving auth identities and storage paths
- replacing vendor-specific functions or policies
- matching production behavior in local/self-hosted environments

When this becomes wrong:
- you need strict cost predictability
- storage/bandwidth is central to the product
- enterprise auth/compliance features become mandatory
- self-hosting or easy vendor exit is a core requirement
```

The key difference: the skill should not reject Supabase by default. It should prevent a recommendation from being based only on homepage positioning or a free-tier headline.
