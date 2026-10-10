#!/usr/bin/env python3
"""Offline unit tests for the manual Discord animal progress reporter."""
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import discord_animal_progress as dashboard


def sample_report():
    players = {}
    for index, name in enumerate(dashboard.PLAYERS):
        collected_cats = list(dashboard.CATS)[:index + 1]
        collected_wolves = list(dashboard.WOLVES)[:index + 1]
        players[name] = {
            "cats": {
                "collected": collected_cats,
                "missing": [key for key in dashboard.CATS if key not in collected_cats],
                "count": len(collected_cats),
                "total": len(dashboard.CATS),
            },
            "wolves": {
                "collected": collected_wolves,
                "missing": [key for key in dashboard.WOLVES if key not in collected_wolves],
                "count": len(collected_wolves),
                "total": len(dashboard.WOLVES),
            },
        }
    return {
        "server": "inno.exaroton.me",
        "read_only": True,
        "server_status_code": 0,
        "players": players,
    }


class DashboardTests(unittest.TestCase):
    def test_embed_contains_all_four_players_and_all_missing_variants(self):
        report = sample_report()
        payload = dashboard.discord_payload(
            report, now=datetime(2026, 10, 9, tzinfo=timezone.utc)
        )
        self.assertEqual(payload["allowed_mentions"], {"parse": []})
        self.assertEqual(len(payload["embeds"]), 1)
        embed = payload["embeds"][0]
        self.assertEqual([f["name"] for f in embed["fields"]],
                         [*dashboard.PLAYERS, "全服合計"])
        self.assertIn("黑貓", embed["fields"][0]["value"])
        self.assertNotIn("虎斑", embed["fields"][0]["value"])
        self.assertIn("全服未收集", embed["fields"][-1]["value"])
        self.assertIn("2026-10-09", embed["timestamp"])
        self.assertIn("OFFLINE", embed["description"])
        self.assertNotIn("@everyone", str(payload))

    def test_unknown_or_missing_progress_never_posts(self):
        report = sample_report()
        del report["players"]["SunnyChen"]
        with self.assertRaises(dashboard.PublishError):
            dashboard.discord_payload(report)
        report = sample_report()
        report["players"]["SunnyChen"]["wolves"]["missing"] = []
        with self.assertRaises(dashboard.PublishError):
            dashboard.discord_payload(report)
        report = sample_report()
        report["read_only"] = False
        with self.assertRaises(dashboard.PublishError):
            dashboard.discord_payload(report)

    def test_cannot_post_to_non_discord_domains(self):
        with self.assertRaises(dashboard.PublishError):
            dashboard.validate_webhook_url(
                "https://evil.example/api/webhooks/123456789012345678/aBcDeF"
            )
        self.assertEqual(
            dashboard.validate_webhook_url(
                "https://discord.com/api/webhooks/123456789012345678/aBcDeF"
            )[1],
            "123456789012345678",
        )

    @patch.object(dashboard, "save_state")
    @patch.object(dashboard, "send_json")
    @patch.object(dashboard, "get_state")
    def test_first_update_creates_once_and_saves_id(self, get_state, send_json, save_state):
        get_state.return_value = ({}, None)
        send_json.return_value = {"id": "1234567890123456789"}
        result = dashboard.publish(
            sample_report(),
            "https://discord.com/api/webhooks/123456789012345678/aBcDeF",
            dashboard.REPOSITORY, "github-token",
        )
        self.assertEqual(result, ("created", "1234567890123456789"))
        self.assertEqual(send_json.call_args.args[0], "POST")
        save_state.assert_called_once_with(
            dashboard.REPOSITORY, "github-token",
            {"webhook_id": "123456789012345678", "message_id": "1234567890123456789"},
            None,
        )

    @patch.object(dashboard, "save_state")
    @patch.object(dashboard, "send_json")
    @patch.object(dashboard, "get_state")
    def test_next_update_edits_original_without_new_post(self, get_state, send_json, save_state):
        get_state.return_value = ({
            "webhook_id": "123456789012345678", "message_id": "1234567890123456789",
        }, "git-content-sha")
        send_json.return_value = {"id": "1234567890123456789"}
        result = dashboard.publish(
            sample_report(),
            "https://discord.com/api/webhooks/123456789012345678/aBcDeF",
            dashboard.REPOSITORY, "github-token",
        )
        self.assertEqual(result, ("updated", "1234567890123456789"))
        self.assertEqual(send_json.call_args.args[0], "PATCH")
        save_state.assert_not_called()

    @patch.object(dashboard, "save_state")
    @patch.object(dashboard, "send_json")
    @patch.object(dashboard, "get_state")
    def test_deleted_message_recreates_and_repairs_state(self, get_state, send_json, save_state):
        get_state.return_value = ({
            "webhook_id": "123456789012345678", "message_id": "1234567890123456789",
        }, "git-content-sha")
        send_json.side_effect = [None, {"id": "9999999999999999999"}]
        result = dashboard.publish(
            sample_report(),
            "https://discord.com/api/webhooks/123456789012345678/aBcDeF",
            dashboard.REPOSITORY, "github-token",
        )
        self.assertEqual(result, ("created", "9999999999999999999"))
        self.assertEqual([call.args[0] for call in send_json.call_args_list], ["PATCH", "POST"])
        save_state.assert_called_once()


if __name__ == "__main__":
    unittest.main()
