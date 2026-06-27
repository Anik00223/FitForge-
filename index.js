import { withSupabase } from "@supabase/server"

export default {
  /**
   * Request handler wrapping the incoming request with Supabase context.
   * Provides:
   *  - ctx.supabase: pre-authenticated client scoped to user's JWT/RLS
   *  - ctx.supabaseAdmin: privileged client bypassing RLS
   */
  fetch: withSupabase({ auth: "user" }, async (req, ctx) => {
    try {
      // Query the database using the user's RLS-scoped client
      const { data, error } = await ctx.supabase
        .from("todos")
        .select("*")
        .limit(10)

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { "Content-Type": "application/json" },
        })
      }

      return Response.json({
        success: true,
        data: data,
        user: ctx.user, // User profile and claims injected by withSupabase
      })
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      })
    }
  }),
}
