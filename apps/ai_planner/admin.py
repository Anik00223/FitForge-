from django.contrib import admin
from apps.ai_planner.models import GeneratedPlan, PlanQA

@admin.register(GeneratedPlan)
class GeneratedPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'is_active', 'generated_at')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('user__username',)
    date_hierarchy = 'generated_at'
    readonly_fields = ('plan_content', 'user_inputs')

@admin.register(PlanQA)
class PlanQAAdmin(admin.ModelAdmin):
    list_display = ('plan', 'question_preview', 'asked_at')
    search_fields = ('question', 'answer')

    def question_preview(self, obj):
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
    question_preview.short_description = 'Question'
