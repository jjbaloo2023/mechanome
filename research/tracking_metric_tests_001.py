"""Hand-constructed regression cases for validate_tracking cohort semantics."""
import numpy as np

from validation.tracking import Track, validate_tracking


def _meta(T):
    return {"T_field": T, "channels": ["coat"]}


def _gt(sid, birth, death, y=10.0, x=10.0):
    return {"sid": sid, "birth": birth, "death": death, "y_px": y, "x_px": x,
            "active_force_pN": 0.0}


def _track(tid, frames, y=10.0, x=10.0):
    return Track(tid, list(frames), [y] * len(frames), [x] * len(frames))


def _movie(T, visible=()):
    movie = np.zeros((T, 1, 30, 30), dtype=float)
    for frame in visible:
        movie[frame, 0, 10, 10] = 30.0
    return movie


def test_ineligible_match_and_eligible_miss_use_separate_cohorts():
    val = validate_tracking([_track(0, [0])], [_gt("a", 0, 2)], _meta(2),
                            movie=_movie(2, visible=[1]))
    assert (val["tp"], val["fp"], val["fn"]) == (1, 0, 1)
    assert val["all_presence"]["recall"] == 0.5
    assert (val["detectable"]["tp"], val["detectable"]["fp"], val["detectable"]["fn"]) == (0, 0, 1)
    assert val["detectable"]["precision"] is None
    assert val["detectable"]["f1"] == 0.0
    assert val["detectable"]["ignored_ineligible_matches"] == 1


def test_extra_missed_ineligible_frame_changes_only_full_cohort():
    val = validate_tracking([_track(0, [0])], [_gt("a", 0, 3)], _meta(3),
                            movie=_movie(3, visible=[1]))
    assert (val["all_presence"]["tp"], val["all_presence"]["fn"]) == (1, 2)
    assert (val["detectable"]["tp"], val["detectable"]["fn"]) == (0, 1)
    assert val["all_presence"]["gt_presence_frames"] == 3
    assert val["detectable"]["eligible_gt_presence_frames"] == 1


def test_all_visible_and_no_movie_fallback_agree():
    gt = [_gt("a", 0, 2)]
    tracks = [_track(0, [0, 1])]
    with_movie = validate_tracking(tracks, gt, _meta(2), movie=_movie(2, visible=[0, 1]))
    no_movie = validate_tracking(tracks, gt, _meta(2))
    for key in ("tp", "fp", "fn", "precision", "recall", "f1"):
        assert with_movie["all_presence"][key] == with_movie["detectable"][key]
    assert no_movie["all_presence"]["tp"] == no_movie["detectable"]["tp"] == 2
    assert no_movie["detectable"]["eligibility_source"] == "all_presence_no_movie_fallback"


def test_all_ineligible_missing_events_and_empty_conditional_rates_are_explicit():
    val = validate_tracking([], [_gt("a", 0, 1), _gt("b", 1, 2)], _meta(2), movie=_movie(2))
    assert (val["all_presence"]["tp"], val["all_presence"]["fn"]) == (0, 2)
    assert val["all_presence"]["gt_events_total"] == 2
    assert val["all_presence"]["gt_events_ever_matched"] == 0
    assert val["detectable"]["eligible_gt_presence_frames"] == 0
    assert val["detectable"]["recall"] is None
    assert val["detectable"]["f1"] is None


def test_empty_truth_and_unmatched_predictions_are_false_positives_in_both_blocks():
    val = validate_tracking([_track(0, [0])], [], _meta(1))
    assert (val["all_presence"]["tp"], val["all_presence"]["fp"], val["all_presence"]["fn"]) == (0, 1, 0)
    assert (val["detectable"]["tp"], val["detectable"]["fp"], val["detectable"]["fn"]) == (0, 1, 0)
    assert val["all_presence"]["recall"] is None
    assert val["recall"] == 0.0  # documented legacy scalar fallback


def test_empty_truth_and_predictions_leave_explicit_rates_undefined():
    val = validate_tracking([], [], _meta(1))
    for block in (val["all_presence"], val["detectable"]):
        assert (block["tp"], block["fp"], block["fn"]) == (0, 0, 0)
        assert block["precision"] is None and block["recall"] is None and block["f1"] is None
    assert val["all_presence"]["gt_event_detected_frac"] is None
    assert (val["precision"], val["recall"], val["f1"]) == (0.0, 0.0, 0.0)
    assert val["gt_detected_frac"] == 0.0


def test_temporally_disjoint_prediction_does_not_match_or_recover_event():
    val = validate_tracking([_track(0, [1])], [_gt("a", 0, 1)], _meta(2), match_radius_px=3)
    assert (val["tp"], val["fp"], val["fn"]) == (0, 1, 1)
    assert val["all_presence"]["gt_events_ever_matched"] == 0
    assert val["gt_detected_frac"] == 0.0


def test_conditional_precision_ignores_ineligible_match_but_counts_true_fp():
    tracks = [_track(0, [0]), _track(1, [1]), _track(2, [1], x=25.0)]
    val = validate_tracking(tracks, [_gt("a", 0, 2)], _meta(2), movie=_movie(2, visible=[0]), match_radius_px=3)
    assert (val["detectable"]["tp"], val["detectable"]["fp"], val["detectable"]["fn"]) == (1, 1, 0)
    assert val["detectable"]["precision"] == 0.5
    assert val["detectable"]["ignored_ineligible_matches"] == 1


def test_duplicate_and_out_of_presence_predictions_are_one_to_one_false_positives():
    tracks = [_track(0, [0]), _track(1, [0]), _track(2, [1])]
    val = validate_tracking(tracks, [_gt("a", 0, 1)], _meta(2), match_radius_px=3)
    assert (val["tp"], val["fp"], val["fn"]) == (1, 2, 0)
    assert val["all_presence"]["gt_events_ever_matched"] == 1


def test_spatial_gate_includes_exact_boundary_and_excludes_just_outside():
    gt = [_gt("a", 0, 1)]
    at_boundary = validate_tracking([_track(0, [0], x=13.0)], gt, _meta(1), match_radius_px=3)
    outside = validate_tracking([_track(0, [0], x=13.0001)], gt, _meta(1), match_radius_px=3)
    assert (at_boundary["tp"], at_boundary["fp"], at_boundary["fn"]) == (1, 0, 0)
    assert (outside["tp"], outside["fp"], outside["fn"]) == (0, 1, 1)
