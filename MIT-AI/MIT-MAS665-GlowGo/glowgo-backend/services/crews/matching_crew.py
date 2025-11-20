"""
Matching Crew - Orchestrates all 5 agents for end-to-end service matching

This crew manages the complete workflow from preference gathering through
final ranking of service providers.
"""

from typing import Dict, Any, List, Optional
import logging

from services.agents.conversation_agent import conversation_agent
from services.agents.quality_assurance_agent import quality_assurance_agent
from services.agents.matching_agent import matching_agent
from services.agents.availability_agent import availability_agent
from services.agents.ranking_agent import ranking_agent


# Configure logging
logger = logging.getLogger(__name__)


class MatchingCrew:
    """
    Production matching crew that orchestrates 5 agents:
    1. ConversationAgent - Gathers preferences naturally
    2. QualityAssuranceAgent - Validates preferences completeness
    3. MatchingAgent - Finds merchant candidates
    4. AvailabilityAgent - Checks time slots
    5. RankingAgent - Ranks options by fit
    """

    def __init__(self):
        """Initialize the matching crew with all agents"""
        self.conversation_agent = conversation_agent
        self.qa_agent = quality_assurance_agent
        self.matching_agent = matching_agent
        self.availability_agent = availability_agent
        self.ranking_agent = ranking_agent

        logger.info("MatchingCrew initialized with 5 agents")

    async def run_preference_gathering(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        current_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 1: Gather and validate user preferences

        Args:
            user_message: Current message from user
            conversation_history: Previous conversation messages
            current_preferences: Already extracted preferences

        Returns:
            dict: {
                "ready_to_match": bool,
                "extracted_preferences": dict,
                "response_to_user": str,
                "next_question": str or None,
                "conversation_context": str
            }
        """
        try:
            # Step 1: Run ConversationAgent to extract preferences
            logger.info(f"Running ConversationAgent with message: {user_message[:50]}...")

            conversation_result = await self.conversation_agent.execute(
                user_message=user_message,
                conversation_history=conversation_history,
                current_preferences=current_preferences
            )

            extracted_preferences = conversation_result.get("extracted_preferences", {})
            ready_to_match = conversation_result.get("ready_to_match", False)
            response_to_user = conversation_result.get("response_to_user", "")
            next_question = conversation_result.get("next_question")
            conversation_context = conversation_result.get("conversation_context", "")

            # Step 2: If ready to match, run QualityAssuranceAgent
            if ready_to_match:
                logger.info("ConversationAgent says ready to match. Running QA validation...")

                qa_result = await self.qa_agent.execute(
                    preferences=extracted_preferences
                )

                # Check validation results
                validation_passed = qa_result.get("validation_passed", False)
                is_valid = qa_result.get("ready_to_proceed", validation_passed)
                issues = qa_result.get("issues", [])

                # Generate clarification message from issues
                if issues and not is_valid:
                    clarification_message = f"I need a bit more information: {issues[0].get('message', 'Please provide more details')}"
                else:
                    clarification_message = None

                if not is_valid:
                    # QA found issues - need more information
                    logger.warning(f"QA validation failed with issues: {issues}")

                    ready_to_match = False
                    response_to_user = clarification_message or "I need a bit more information."

                    # Extract which field needs clarification
                    if issues:
                        next_question = issues[0].get("field")
                else:
                    logger.info("QA validation passed. Ready to proceed to matching.")

            return {
                "ready_to_match": ready_to_match,
                "extracted_preferences": extracted_preferences,
                "response_to_user": response_to_user,
                "next_question": next_question,
                "conversation_context": conversation_context
            }

        except Exception as e:
            logger.error(f"Error in preference gathering: {e}", exc_info=True)

            # Fallback response
            return {
                "ready_to_match": False,
                "extracted_preferences": current_preferences,
                "response_to_user": "I'd love to help! What service are you looking for?",
                "next_question": "service_type",
                "conversation_context": ""
            }

    async def run(
        self,
        preferences: Dict[str, Any],
        location: str = "Cambridge, MA"
    ) -> Dict[str, Any]:
        """
        Simple run method for matching, checking availability, and ranking providers

        This is a simplified interface that follows the standard crew pattern.
        For more control, use run_matching_and_ranking() instead.

        Args:
            preferences: User preferences dict containing:
                - service_type: str (required)
                - budget_min: float (optional)
                - budget_max: float (optional)
                - time_urgency: str (optional: "ASAP", "today", "week", "flexible")
                - location: str (optional, overridden by location parameter)
            location: Location string (default: "Cambridge, MA")

        Returns:
            dict: {
                "ranked_options": [
                    {
                        "rank": int,
                        "merchant_id": str,
                        "merchant_name": str,
                        "service_type": str,
                        "distance": float,
                        "price": float,
                        "rating": float (0-5),
                        "reviews": int,
                        "available_times": [str],
                        "why_recommended": str,
                        "relevance_score": float (0-1)
                    }
                ],
                "total_options_found": int,
                "search_summary": str
            }
        """
        # Add location to preferences if passed separately
        # This ensures the matching agent can filter by city (Boston/Cambridge)
        if location and not preferences.get("location"):
            # Extract just the city name from "Boston, MA" or "Cambridge, MA"
            city = location.split(",")[0].strip()
            preferences["location"] = city

        # For now, we'll use a default location (can be enhanced with geocoding)
        # This simplified version doesn't require exact coordinates
        user_location = None  # Let the matching agent handle location-based filtering

        # Call the comprehensive method
        return await self.run_matching_and_ranking(
            preferences=preferences,
            user_location=user_location,
            max_distance=10.0
        )

    async def run_matching_and_ranking(
        self,
        preferences: Dict[str, Any],
        user_location: Optional[Dict[str, float]] = None,
        max_distance: float = 10.0
    ) -> Dict[str, Any]:
        """
        Phase 2: Find, check availability, and rank service providers

        Args:
            preferences: User preferences dict containing:
                - service_type: str
                - budget_min: float (optional)
                - budget_max: float (optional)
                - time_urgency: str (ASAP, today, week, flexible)
                - artisan_preference: str (optional)
            user_location: {"lat": float, "lon": float} (optional)
            max_distance: Maximum search distance in miles

        Returns:
            dict: {
                "ranked_options": [
                    {
                        "rank": int,
                        "merchant_id": str,
                        "merchant_name": str,
                        "service_name": str,
                        "service_type": str,
                        "distance": float,
                        "price": float,
                        "available_times": [str],
                        "rating": float,
                        "why_recommended": str,
                        "relevance_score": float
                    }
                ],
                "total_options_found": int,
                "search_summary": str
            }
        """
        try:
            # Step 1: Run MatchingAgent to find candidates
            logger.info(f"Running MatchingAgent with preferences: {preferences.get('service_type')}")

            matching_result = await self.matching_agent.execute(
                preferences=preferences,
                user_location=user_location,
                max_distance=max_distance
            )

            if matching_result.get("status") != "success":
                logger.warning(f"MatchingAgent returned non-success: {matching_result.get('message')}")

                return {
                    "ranked_options": [],
                    "total_options_found": 0,
                    "search_summary": matching_result.get("message", "No providers found matching your criteria.")
                }

            candidates = matching_result.get("candidates", [])
            candidate_count = matching_result.get("candidate_count", 0)

            if candidate_count == 0:
                # Generate intelligent fallback suggestions
                fallback_suggestions = await self._generate_fallback_suggestions(preferences, user_location, max_distance)

                return {
                    "ranked_options": [],
                    "total_options_found": 0,
                    "search_summary": fallback_suggestions["message"],
                    "suggestions": fallback_suggestions.get("suggestions", []),
                    "alternative_matches": fallback_suggestions.get("alternative_matches", [])
                }

            logger.info(f"MatchingAgent found {candidate_count} candidates")

            # Step 2: Run AvailabilityAgent to check time slots
            logger.info("Running AvailabilityAgent to check availability...")

            time_urgency = preferences.get("time_urgency", "flexible")
            preferred_date = preferences.get("preferred_date")
            preferred_time = preferences.get("preferred_time")
            time_constraint = preferences.get("time_constraint")

            availability_result = await self.availability_agent.execute(
                candidates=candidates,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                time_constraint=time_constraint,
                time_urgency=time_urgency
            )

            available_providers = availability_result.get("candidates_with_slots", [])
            available_count = availability_result.get("providers_available", 0)

            if available_count == 0:
                logger.warning("No providers have availability")

                # Generate intelligent fallback suggestions for availability
                fallback_suggestions = await self._generate_availability_fallback(
                    candidates, preferences, user_location
                )

                return {
                    "ranked_options": [],
                    "total_options_found": candidate_count,
                    "search_summary": fallback_suggestions["message"],
                    "suggestions": fallback_suggestions.get("suggestions", []),
                    "alternative_matches": fallback_suggestions.get("alternative_matches", [])
                }

            logger.info(f"AvailabilityAgent found {available_count} available providers")

            # Step 3: Run RankingAgent to rank by fit
            logger.info("Running RankingAgent to rank providers...")

            ranking_result = await self.ranking_agent.execute(
                candidates=available_providers,
                user_preferences=preferences,
                user_location=user_location
            )

            ranked_providers = ranking_result.get("ranked_providers", [])

            if not ranked_providers:
                logger.warning("RankingAgent returned no ranked providers")

                return {
                    "ranked_options": [],
                    "total_options_found": available_count,
                    "search_summary": f"Found {available_count} available providers but couldn't rank them."
                }

            logger.info(f"RankingAgent ranked {len(ranked_providers)} providers")

            # Format output
            ranked_options = []

            for rank, provider in enumerate(ranked_providers[:10], start=1):
                # Format available times as time strings
                available_slots = provider.get("available_slots", [])
                formatted_times = []
                for slot in available_slots[:5]:  # First 5 slots
                    if isinstance(slot, dict):
                        time_str = slot.get("time", slot.get("datetime", ""))
                        formatted_times.append(time_str)
                    else:
                        formatted_times.append(str(slot))

                ranked_options.append({
                    "rank": rank,
                    "merchant_id": provider.get("provider_id"),
                    "merchant_name": provider.get("provider_name"),
                    "service_name": provider.get("service_name"),
                    "service_type": preferences.get("service_type"),
                    "distance": round(provider.get("distance_miles", 0), 1) if provider.get("distance_miles") else None,
                    "price": float(provider.get("price", 0)),
                    "rating": float(provider.get("rating", 0)),
                    "reviews": int(provider.get("review_count", 0)),
                    "available_times": formatted_times,
                    "why_recommended": provider.get("recommendation_reason", "Great match for your needs"),
                    "relevance_score": round(provider.get("overall_score", 0) / 100, 2),  # Convert to 0-1 scale

                    # Enhanced fields for real provider data
                    "photo_url": provider.get("photo_url", ""),
                    "photos": provider.get("photos", []),
                    "address": provider.get("address", ""),
                    "city": provider.get("city", ""),
                    "state": provider.get("state", ""),
                    "phone": provider.get("phone", ""),
                    "price_range": provider.get("price_range", ""),
                    "specialties": provider.get("specialties", []),
                    "stylist_names": provider.get("stylist_names", []),
                    "booking_url": provider.get("booking_url", ""),
                    "bio": provider.get("bio", ""),
                    "yelp_url": provider.get("yelp_url", "")
                })

            search_summary = (
                f"Found {len(ranked_options)} excellent matches! "
                f"Top choice: {ranked_options[0]['merchant_name']} "
                f"(${ranked_options[0]['price']}, {ranked_options[0]['rating']}⭐)"
            )

            return {
                "ranked_options": ranked_options,
                "total_options_found": len(ranked_options),
                "search_summary": search_summary
            }

        except Exception as e:
            logger.error(f"Error in matching and ranking: {e}", exc_info=True)

            # Fallback response
            return {
                "ranked_options": [],
                "total_options_found": 0,
                "search_summary": f"An error occurred during matching: {str(e)}"
            }

    async def run_complete_flow(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        current_preferences: Dict[str, Any],
        user_location: Optional[Dict[str, float]] = None,
        max_distance: float = 10.0
    ) -> Dict[str, Any]:
        """
        Run complete flow: preference gathering + matching + ranking

        This is a convenience method that runs both phases if ready to match.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            current_preferences: Already extracted preferences
            user_location: User coordinates (optional)
            max_distance: Search radius in miles

        Returns:
            dict: Combined result from both phases
        """
        try:
            # Phase 1: Gather preferences
            gathering_result = await self.run_preference_gathering(
                user_message=user_message,
                conversation_history=conversation_history,
                current_preferences=current_preferences
            )

            # If not ready to match, return just the gathering result
            if not gathering_result.get("ready_to_match"):
                return {
                    "phase": "preference_gathering",
                    "ready_to_match": False,
                    "response_to_user": gathering_result.get("response_to_user"),
                    "next_question": gathering_result.get("next_question"),
                    "extracted_preferences": gathering_result.get("extracted_preferences")
                }

            # Phase 2: Match and rank
            logger.info("Preferences complete. Running matching and ranking...")

            matching_result = await self.run_matching_and_ranking(
                preferences=gathering_result.get("extracted_preferences"),
                user_location=user_location,
                max_distance=max_distance
            )

            return {
                "phase": "matching_complete",
                "ready_to_match": True,
                "extracted_preferences": gathering_result.get("extracted_preferences"),
                "ranked_options": matching_result.get("ranked_options", []),
                "total_options_found": matching_result.get("total_options_found", 0),
                "search_summary": matching_result.get("search_summary", "")
            }

        except Exception as e:
            logger.error(f"Error in complete flow: {e}", exc_info=True)

            return {
                "phase": "error",
                "ready_to_match": False,
                "response_to_user": "I encountered an error. Please try again.",
                "next_question": None,
                "extracted_preferences": current_preferences
            }

    async def _generate_fallback_suggestions(
        self,
        preferences: Dict[str, Any],
        user_location: Optional[Dict[str, float]],
        max_distance: float
    ) -> Dict[str, Any]:
        """
        Generate intelligent suggestions when no matches are found

        This method tries relaxing constraints one at a time to find what adjustments
        would yield results.

        Args:
            preferences: Original user preferences
            user_location: User's location
            max_distance: Current search radius

        Returns:
            dict: {
                "message": str (user-friendly explanation),
                "suggestions": [str] (list of adjustment suggestions),
                "alternative_matches": [dict] (providers that would match with adjustments)
            }
        """
        try:
            suggestions = []
            alternative_matches = []

            # Try relaxing budget constraint
            if preferences.get("budget_max"):
                relaxed_budget_prefs = preferences.copy()
                budget_increase = preferences["budget_max"] * 0.3  # 30% increase
                relaxed_budget_prefs["budget_max"] = preferences["budget_max"] + budget_increase

                # Quick check without full matching flow
                from services.tools.matching_tools import service_filter_tool, budget_filter_tool

                service_results = service_filter_tool.execute({
                    "service_type": preferences.get("service_type")
                })

                if service_results.get("count", 0) > 0:
                    budget_results = budget_filter_tool.execute({
                        "budget_max": relaxed_budget_prefs["budget_max"],
                        "budget_min": relaxed_budget_prefs.get("budget_min"),
                        "services": service_results.get("matching_services", [])
                    })

                    if budget_results.get("count", 0) > 0:
                        cheapest = min(
                            budget_results["affordable_services"],
                            key=lambda x: x.get("base_price", float('inf'))
                        )
                        suggestions.append(
                            f"If you raise your budget to ${cheapest['base_price']:.0f}, "
                            f"{cheapest['merchant_name']} would be available"
                        )
                        alternative_matches.append({
                            "provider_name": cheapest["merchant_name"],
                            "price": cheapest["base_price"],
                            "adjustment_needed": "budget",
                            "new_budget": cheapest["base_price"]
                        })

            # Try relaxing time constraint
            if preferences.get("preferred_date") or preferences.get("time_urgency"):
                # Suggest flexible timing
                relaxed_time_prefs = preferences.copy()
                relaxed_time_prefs["time_urgency"] = "flexible"
                relaxed_time_prefs.pop("preferred_date", None)
                relaxed_time_prefs.pop("preferred_time", None)
                relaxed_time_prefs.pop("time_constraint", None)

                # Quick availability check
                from services.tools.matching_tools import service_filter_tool
                service_results = service_filter_tool.execute({
                    "service_type": preferences.get("service_type")
                })

                if service_results.get("count", 0) > 0:
                    # Check if budget filter passes with flexible timing
                    from services.tools.matching_tools import budget_filter_tool
                    budget_results = budget_filter_tool.execute({
                        "budget_max": preferences.get("budget_max"),
                        "budget_min": preferences.get("budget_min"),
                        "services": service_results.get("matching_services", [])
                    })

                    if budget_results.get("count", 0) > 0:
                        preferred_date_str = preferences.get("preferred_date", "your preferred time")
                        suggestions.append(
                            f"If you're flexible with timing (not strict about {preferred_date_str}), "
                            f"{budget_results['count']} provider(s) would be available"
                        )

            # Try expanding location radius
            if user_location and max_distance < 25:
                expanded_distance = max_distance + 10
                suggestions.append(
                    f"If you expand your search radius to {expanded_distance} miles, "
                    f"more providers might be available"
                )

            # Build user-friendly message
            if suggestions:
                message = (
                    f"I couldn't find exact matches for your criteria. Here are some options:\n\n"
                    + "\n".join(f"• {s}" for s in suggestions[:3])  # Top 3 suggestions
                )

                if not alternative_matches:
                    message += "\n\nWould you like to adjust any of these criteria?"
            else:
                message = (
                    "Unfortunately, I couldn't find any providers matching your criteria. "
                    "This might be because:\n"
                    "• The service type might not be available in your area\n"
                    "• Your budget or timing constraints are very specific\n\n"
                    "Would you like to try a different service or adjust your preferences?"
                )

            return {
                "message": message,
                "suggestions": suggestions,
                "alternative_matches": alternative_matches
            }

        except Exception as e:
            logger.error(f"Error generating fallback suggestions: {e}", exc_info=True)
            return {
                "message": "No providers found. Try adjusting your budget, timing, or location.",
                "suggestions": [],
                "alternative_matches": []
            }

    async def _generate_availability_fallback(
        self,
        candidates: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        user_location: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Generate suggestions when providers are found but none have availability

        Args:
            candidates: List of matched providers (without availability)
            preferences: User preferences
            user_location: User's location

        Returns:
            dict: {
                "message": str,
                "suggestions": [str],
                "alternative_matches": [dict]
            }
        """
        try:
            suggestions = []
            alternative_matches = []

            # Extract time preferences
            preferred_date = preferences.get("preferred_date")
            preferred_time = preferences.get("preferred_time")
            time_constraint = preferences.get("time_constraint")

            # Suggest alternative timing
            if preferred_date:
                from datetime import datetime, timedelta
                target_date = datetime.fromisoformat(preferred_date)

                # Suggest day before
                day_before = (target_date - timedelta(days=1)).date().isoformat()
                suggestions.append(
                    f"Try the day before ({day_before}) for better availability"
                )

                # Suggest day after
                day_after = (target_date + timedelta(days=1)).date().isoformat()
                suggestions.append(
                    f"Try the day after ({day_after}) for more options"
                )

            if time_constraint:
                # Suggest removing time constraint
                suggestions.append(
                    f"Consider removing the '{time_constraint}' time constraint for more flexibility"
                )

            if preferred_time:
                # Suggest different time of day
                from datetime import datetime
                time_obj = datetime.strptime(preferred_time, "%H:%M")
                hour = time_obj.hour

                if hour < 12:
                    suggestions.append("Try afternoon or evening slots (after 12pm)")
                else:
                    suggestions.append("Try morning slots (before 12pm)")

            # Suggest flexible timing
            if not suggestions:
                suggestions.append("Try 'flexible' timing to see all available slots")

            # Show top candidates that would be available with adjustments
            for candidate in candidates[:3]:
                alternative_matches.append({
                    "provider_name": candidate.get("merchant_name", "Provider"),
                    "price": candidate.get("base_price"),
                    "rating": candidate.get("merchant_rating"),
                    "adjustment_needed": "timing",
                    "message": f"{candidate.get('merchant_name')} has availability at other times"
                })

            # Build message
            message = (
                f"Found {len(candidates)} great providers, but none have availability for your exact timing.\n\n"
                "Here are some suggestions:\n"
                + "\n".join(f"• {s}" for s in suggestions[:3])
            )

            if alternative_matches:
                message += "\n\nProviders with availability at other times:\n"
                for match in alternative_matches:
                    message += f"• {match['provider_name']} (${match['price']}, {match['rating']}⭐)\n"

            return {
                "message": message,
                "suggestions": suggestions,
                "alternative_matches": alternative_matches
            }

        except Exception as e:
            logger.error(f"Error generating availability fallback: {e}", exc_info=True)
            return {
                "message": "No availability found. Try flexible timing or different dates.",
                "suggestions": [],
                "alternative_matches": []
            }


# Global crew instance for easy import
matching_crew = MatchingCrew()
