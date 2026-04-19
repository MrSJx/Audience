from app.core.config import settings
from app.models.analysis import AudienceReactionReport, MediaAnalysisResult, PeakMoment
from app.models.contracts import UploadContract
from app.models.platforms import SupportedMediaType, TargetPlatform
from app.models.simulation import (
    AgeBand,
    AudienceAgentDefinition,
    AudiencePanelDefinition,
    AudiencePreset,
    CombinedPanelOutput,
    ConsentRequirement,
    EmotionScorecard,
    ExperienceLevel,
    GenderLens,
    SimulationFinalReport,
    SimulationMediaType,
    SimulationRunContract,
    SimulationRunMode,
    SimulationRuntimeLimit,
    SimulationStatus,
    SimulationTarget,
    SimulationTargetPlatform,
    TimelineSpike,
)
from app.services.llm_service import LLMServiceError, generate_report_with_llama
from app.services.parser_service import parse_report_payload


def get_starter_report_shape() -> dict[str, object]:
    """Expose the intended MVP report contract as a starter reference."""
    return AudienceReactionReport(
        platform=TargetPlatform.INSTAGRAM_REELS,
        content_summary="Starter report shape for the Audience MVP.",
        hook_score=0,
        engagement_score=0,
        boring_rate=0,
        peak_moments=[PeakMoment(timestamp="0:00", event="starter placeholder")],
        simulated_comments=["This is a starter placeholder comment."],
        final_verdict="Starter placeholder verdict.",
        improvements=["Replace placeholders with generated report logic."],
    ).model_dump(mode="json")


def get_phase_two_contract() -> dict[str, object]:
    """Return the canonical Phase 2 request, response, and upload contract."""
    request_example = {
        "platform": TargetPlatform.INSTAGRAM_REELS.value,
        "media_type": SupportedMediaType.IMAGE.value,
        "filename": "monday-reel-cover.jpg",
        "mime_type": "image/jpeg",
        "file_size_bytes": 180432,
        "caption": "POV: Monday starts with chaos.",
        "duration_seconds": None,
    }

    response_example = AudienceReactionReport(
        platform=TargetPlatform.INSTAGRAM_REELS,
        content_summary=(
            "A comedic Instagram-ready visual with a fast, attention-grabbing "
            "premise and clear meme energy."
        ),
        hook_score=74,
        engagement_score=68,
        boring_rate=29,
        peak_moments=[
            PeakMoment(timestamp="0:00", event="strong visual opener"),
            PeakMoment(timestamp="0:06", event="attention may soften if pacing dips"),
        ],
        simulated_comments=[
            "The first second grabbed me immediately.",
            "Funny setup, but the middle beat could be tighter.",
        ],
        final_verdict=(
            "Strong opening concept for Instagram Reels, with the best chance "
            "of success when the central beat stays concise."
        ),
        improvements=[
            "Front-load the clearest emotional beat.",
            "Trim any slower middle section.",
        ],
    ).model_dump(mode="json")

    return {
        "first_user_flow": {
            "supported_platform": TargetPlatform.INSTAGRAM_REELS.value,
            "supported_media_types": [
                SupportedMediaType.IMAGE.value,
                SupportedMediaType.SHORT_VIDEO.value,
            ],
            "steps": [
                "User selects Instagram Reels as the target platform.",
                "User uploads one image or one short video.",
                "Backend validates the file and extracts media signals.",
                "Backend generates a structured audience reaction report.",
                "Frontend renders the report and suggested improvements.",
            ],
        },
        "request_example": request_example,
        "response_example": response_example,
        "upload_contract": UploadContract().model_dump(mode="json"),
    }


def generate_report_from_analysis(analysis: MediaAnalysisResult) -> AudienceReactionReport:
    try:
        return generate_report_with_llama(analysis)
    except LLMServiceError:
        if not settings.use_heuristic_fallback:
            raise

    candidate_payload = _build_heuristic_candidate_report_payload(analysis)
    return parse_report_payload(candidate_payload)


def _build_heuristic_candidate_report_payload(analysis: MediaAnalysisResult) -> dict[str, object]:
    hook_score = _clamp_score(
        round(
            analysis.contrast_score * 0.35
            + analysis.saturation_score * 0.25
            + min(len(analysis.summary_cues) * 4, 20)
            + analysis.scene_change_ratio * 20
        )
    )
    engagement_score = _clamp_score(
        round(
            hook_score * 0.45
            + analysis.brightness_score * 0.15
            + analysis.contrast_score * 0.15
            + analysis.saturation_score * 0.15
            + (10 if analysis.detected_text_present else 0)
            + (5 if analysis.detected_faces > 0 else 0)
        )
    )
    boring_rate = _clamp_score(
        round(100 - (engagement_score * 0.7 + min(hook_score, 80) * 0.2 + 10))
    )

    peak_moments = _build_peak_moments(analysis)
    improvements = _build_improvements(analysis)

    return {
        "platform": analysis.platform.value,
        "content_summary": _build_content_summary(analysis),
        "hook_score": hook_score,
        "engagement_score": engagement_score,
        "boring_rate": boring_rate,
        "peak_moments": [moment.model_dump(mode="json") for moment in peak_moments],
        "simulated_comments": _build_simulated_comments(analysis, hook_score, boring_rate),
        "final_verdict": _build_final_verdict(hook_score, engagement_score, boring_rate),
        "improvements": improvements,
    }


def get_phase_three_and_four_snapshot() -> dict[str, object]:
    analysis_example = MediaAnalysisResult.model_config["json_schema_extra"]["example"]
    report_example = AudienceReactionReport.model_config["json_schema_extra"]["example"]

    return {
        "phase": 4,
        "analysis_result_example": analysis_example,
        "report_schema_example": report_example,
        "report_fields": [
            "platform",
            "content_summary",
            "hook_score",
            "engagement_score",
            "boring_rate",
            "peak_moments",
            "simulated_comments",
            "final_verdict",
            "improvements",
        ],
    }


def get_phase_eleven_contract_snapshot() -> dict[str, object]:
    runtime_limits = [
        SimulationRuntimeLimit(
            mode=SimulationRunMode.QUICK,
            max_agents=3,
            max_video_duration_seconds=30,
            max_audio_duration_seconds=30,
            notes=[
                "Fastest preview mode for laptop testing.",
                "Best for generic panels and short feedback loops.",
            ],
        ),
        SimulationRuntimeLimit(
            mode=SimulationRunMode.STANDARD,
            max_agents=6,
            max_video_duration_seconds=60,
            max_audio_duration_seconds=60,
            notes=[
                "Default balance between coverage and local runtime cost.",
                "Recommended for most serious pre-upload checks.",
            ],
        ),
        SimulationRuntimeLimit(
            mode=SimulationRunMode.DEEP,
            max_agents=8,
            max_video_duration_seconds=90,
            max_audio_duration_seconds=90,
            notes=[
                "Highest local cost mode.",
                "Use when disagreement analysis matters more than speed.",
            ],
        ),
        SimulationRuntimeLimit(
            mode=SimulationRunMode.CUSTOM,
            max_agents=12,
            max_video_duration_seconds=90,
            max_audio_duration_seconds=90,
            notes=[
                "Advanced mode for explicit agent selection.",
                "Sensitive lenses must remain opt-in and consent-gated.",
            ],
        ),
    ]

    request_example = {
        "schema_version": "simulation_request_v2",
        "target": SimulationTarget(
            platform=SimulationTargetPlatform.INSTAGRAM_REELS,
            media_type=SimulationMediaType.SHORT_VIDEO,
            creator_goal="Check whether the opening joke lands quickly enough for short-form viewing.",
        ).model_dump(mode="json"),
        "panel": AudiencePanelDefinition(
            mode=SimulationRunMode.CUSTOM,
            preset=AudiencePreset.CUSTOM,
            requested_agent_count=3,
            agents=[
                AudienceAgentDefinition(
                    label="Minor viewer",
                    age_band=AgeBand.UNDER_18,
                    gender=GenderLens.UNSPECIFIED,
                    experience_level=ExperienceLevel.ACTIVE_SCROLLER,
                    market_context="South Asia short-form audience",
                ),
                AudienceAgentDefinition(
                    label="18+ female viewer",
                    age_band=AgeBand.AGE_18_PLUS,
                    gender=GenderLens.FEMALE,
                    experience_level=ExperienceLevel.CASUAL_VIEWER,
                    market_context="Urban comedy audience",
                ),
                AudienceAgentDefinition(
                    label="18+ male creator lens",
                    age_band=AgeBand.AGE_18_PLUS,
                    gender=GenderLens.MALE,
                    experience_level=ExperienceLevel.CREATOR,
                    market_context="South Asia",
                    sensitive_lenses=[],
                ),
            ],
        ).model_dump(mode="json"),
        "consent_inputs": [
            {
                "consent_key": "religion_lens_ack",
                "granted": False,
            }
        ],
    }

    report_example = SimulationRunContract(
        schema_version="simulation_run_v2",
        status=SimulationStatus.PLANNED,
        target=SimulationTarget(
            platform=SimulationTargetPlatform.INSTAGRAM_REELS,
            media_type=SimulationMediaType.SHORT_VIDEO,
            creator_goal="Predict whether the first five seconds feel funny enough to stop the scroll.",
        ),
        panel=AudiencePanelDefinition(
            mode=SimulationRunMode.CUSTOM,
            preset=AudiencePreset.CUSTOM,
            requested_agent_count=2,
            agents=[
                AudienceAgentDefinition(
                    label="Minor viewer",
                    age_band=AgeBand.UNDER_18,
                    gender=GenderLens.UNSPECIFIED,
                    experience_level=ExperienceLevel.ACTIVE_SCROLLER,
                    market_context="South Asia short-form audience",
                ),
                AudienceAgentDefinition(
                    label="18+ female viewer",
                    age_band=AgeBand.AGE_18_PLUS,
                    gender=GenderLens.FEMALE,
                    experience_level=ExperienceLevel.CASUAL_VIEWER,
                    market_context="Urban comedy audience",
                ),
            ],
        ),
        consent_requirements=[
            ConsentRequirement(
                consent_key="religion_lens_ack",
                title="Sensitive audience lens",
                disclosure_text=(
                    "Religion-based lenses are optional context simulations and must never "
                    "be treated as factual claims about real people."
                ),
                required=True,
                triggered_by=["religion"],
            )
        ],
        per_agent_outputs=[],
        combined_output=CombinedPanelOutput(
            agreement_level=64,
            combined_scorecard=EmotionScorecard(
                happiness=66,
                sadness=9,
                laughter=63,
                surprise=42,
                confusion=18,
                tension=14,
                boredom=27,
            ),
            panel_summary=(
                "The panel agrees on a strong early comedic beat, with mild concern that the "
                "middle section may lose energy."
            ),
        ),
        timeline_spikes=[
            TimelineSpike(
                timestamp="0:03",
                emotion="laughter",
                intensity=78,
                reason="The first joke resolves clearly and early.",
            )
        ],
        final_report=SimulationFinalReport(
            executive_summary=(
                "This contract snapshot shows how a future multi-agent run will separate "
                "panel setup, agent outputs, consent requirements, and combined reporting."
            ),
            strengths=[
                "Clear separation between media target, panel definition, and report output.",
                "Supports both generic presets and custom agent panels.",
            ],
            risks=[
                "Sensitive lenses must remain explicit and auditable.",
                "Large agent counts will require careful local runtime controls.",
            ],
            improvements=[
                "Use quick mode for preview runs on weaker laptops.",
                "Only request sensitive lenses when the user explicitly opts in.",
            ],
            confidence_note=(
                "Simulation outputs are predictive guidance rather than certainty about real "
                "audience behavior."
            ),
        ),
    ).model_dump(mode="json")

    return {
        "phase": 11,
        "contract_name": "Simulation 2.0",
        "supported_run_modes": [mode.value for mode in SimulationRunMode],
        "supported_target_platforms": [platform.value for platform in SimulationTargetPlatform],
        "supported_media_types": [media_type.value for media_type in SimulationMediaType],
        "runtime_limits": [limit.model_dump(mode="json") for limit in runtime_limits],
        "request_example": request_example,
        "response_example": report_example,
        "notes": [
            "Generic and custom audience panels are both first-class concepts in the v2 contract.",
            "Sensitive audience lenses must remain opt-in and consent-gated.",
            "The contract is frozen before the full multi-agent runtime is implemented.",
        ],
    }


def _build_content_summary(analysis: MediaAnalysisResult) -> str:
    article = "An" if analysis.media_type == SupportedMediaType.IMAGE else "A"
    media_label = "image" if analysis.media_type == SupportedMediaType.IMAGE else "short video"
    cue_summary = ", ".join(analysis.summary_cues[:3])
    return (
        f"{article} {media_label} built for Instagram Reels with {analysis.pacing_hint}, "
        f"guided by cues such as {cue_summary}."
    )


def _build_peak_moments(analysis: MediaAnalysisResult) -> list[PeakMoment]:
    if not analysis.extracted_frames:
        return [PeakMoment(timestamp="0:00", event="limited sampling data available")]

    strongest_frame = max(
        analysis.extracted_frames,
        key=lambda frame: frame.brightness_score + frame.contrast_score,
    )
    moments = [
        PeakMoment(timestamp=strongest_frame.timestamp, event="strongest visual attention point")
    ]

    if analysis.scene_change_ratio >= 0.3 and len(analysis.extracted_frames) > 1:
        moments.append(
            PeakMoment(
                timestamp=analysis.extracted_frames[-1].timestamp,
                event="pacing shift likely noticeable by viewers",
            )
        )

    return moments


def _build_simulated_comments(
    analysis: MediaAnalysisResult, hook_score: int, boring_rate: int
) -> list[str]:
    comments = [
        (
            "The opening visual feels strong."
            if hook_score >= 70
            else "The concept is there, but the opening could hit harder."
        ),
        (
            "The pacing stays easy to follow."
            if analysis.pacing_hint != "slow pacing"
            else "It may need a tighter middle to hold attention."
        ),
    ]

    if analysis.detected_text_present:
        comments.append("The on-screen text or graphic detail gives it extra context.")
    if boring_rate >= 45:
        comments.append("I might scroll if the strongest beat does not arrive quickly.")

    return comments[:4]


def _build_final_verdict(hook_score: int, engagement_score: int, boring_rate: int) -> str:
    if hook_score >= 70 and engagement_score >= 70 and boring_rate <= 35:
        return "Strong early audience potential with a believable chance to hold attention."
    if boring_rate >= 50:
        return "Promising idea, but it needs tighter pacing or a sharper opening to reduce likely drop-off."
    return "Solid foundation with room to strengthen retention, clarity, and emotional payoff."


def _build_improvements(analysis: MediaAnalysisResult) -> list[str]:
    improvements: list[str] = []

    if analysis.pacing_hint == "slow pacing":
        improvements.append("Tighten the middle section so the strongest beat arrives sooner.")
    if analysis.detected_text_present:
        improvements.append("Keep any on-screen text concise so it supports rather than slows the visual.")
    if analysis.saturation_score < 35:
        improvements.append("Consider slightly stronger color contrast to improve stop-scroll impact.")
    if analysis.detected_faces == 0 and analysis.media_type == SupportedMediaType.SHORT_VIDEO:
        improvements.append("Introduce a clearer focal subject in the sampled frames.")
    if analysis.brightness_score <= 30:
        improvements.append("Lift brightness slightly if you want the first frame to read more clearly on mobile.")
    if analysis.contrast_score <= 25:
        improvements.append("Increase visual separation between key elements so the hook reads faster.")

    if not improvements:
        improvements.append("Preserve the current visual strengths while testing a sharper first second.")

    return improvements[:3]


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))
