# -*- coding: utf-8 -*-
"""阻力与功率（7.3 v0）：摩擦线解析对照、四维插值、试航反解。"""
import json
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)

import resistance as R  # noqa: E402


def synth_table():
    """合成四维表：值 = 10·Cp + B/T + 1000·∇/L³ + 10·Fn（**对四个自变量都线性**）。
    多线性插值对线性函数应精确 —— 用它锚住插值不写错。"""
    cps = [0.50, 0.70]
    bts = [2.0, 3.0]
    vols = [0.002, 0.003]
    fns = [0.20, 0.30]

    def f(cp, bt, v, fn):
        return 10.0 * cp + bt + 1000.0 * v + 10.0 * fn

    grid = [[[[f(cp, bt, v, fn) for fn in fns] for v in vols] for bt in bts] for cp in cps]
    return {"axes": {"cp": cps, "bt": bts, "volumetric": vols, "fn": fns},
            "grid_order": ["cp", "bt", "volumetric", "fn"], "cr": grid,
            "source": "合成表（测试用）"}


class TestSchoenherr(unittest.TestCase):
    def test_exact_at_1e9(self):
        """Cf = 0.4631 / (lg 1e9)^2.6 = 0.4631 / 9^2.6。"""
        self.assertAlmostEqual(R.schoenherr_cf(1e9)["values"]["cf"],
                               0.4631 / (9.0 ** 2.6), places=12)

    def test_too_small_raises(self):
        with self.assertRaises(ValueError):
            R.schoenherr_cf(1e4)

    def test_out_of_range_warns(self):
        self.assertTrue(R.schoenherr_cf(1e12)["warnings"])

    def test_agrees_with_ittc1957(self):
        """两条摩擦线在实船雷诺数量级应相差 <3%（QM Rn≈2.6e9：实测 −0.3%）。"""
        rn = 2.592e9
        a = R.schoenherr_cf(rn)["values"]["cf"]
        b = R.ittc1957_cf(rn)
        self.assertLess(abs(a - b) / b, 0.03)


class TestFrictionResistance(unittest.TestCase):
    def test_definition_exact(self):
        v, L, S, nu, rho = 10.0, 100.0, 2000.0, 1e-6, 1025.0
        cf = R.schoenherr_cf(v * L / nu)["values"]["cf"]
        r = R.friction_resistance(v, L, S, nu=nu, rho=rho)
        self.assertAlmostEqual(r["values"]["rn"], 1e9, places=6)
        self.assertAlmostEqual(r["values"]["rf_n"],
                               0.5 * rho * S * cf * v * v, places=6)

    def test_roughness_adds_delta_cf(self):
        a = R.friction_resistance(10.0, 100.0, 2000.0, nu=1e-6, delta_cf=0.0)
        b = R.friction_resistance(10.0, 100.0, 2000.0, nu=1e-6,
                                  delta_cf=R.DELTA_CF_TAYLOR)
        self.assertAlmostEqual(b["values"]["cf_total"],
                               a["values"]["cf"] + R.DELTA_CF_TAYLOR, places=12)
        self.assertGreater(b["values"]["rf_n"], a["values"]["rf_n"])

    def test_bad_inputs_raise(self):
        for kw in ({"v_mps": 0}, {"l_wl_m": -1}, {"s_m2": 0}, {"nu": 0}):
            args = dict(v_mps=10.0, l_wl_m=100.0, s_m2=2000.0, nu=1e-6)
            args.update(kw)
            with self.assertRaises(ValueError):
                R.friction_resistance(**args)


class TestResidualTable(unittest.TestCase):
    def test_missing_table_gives_none_and_warns(self):
        """没图谱就置空 —— **绝不照抄 OCR 乱码**。"""
        r = R.residual_from_table(None, 0.6, 3.0, 0.002, 0.3)
        self.assertIsNone(r["values"]["cr"])
        self.assertTrue(any("OCR" in w for w in r["warnings"]))

    def test_node_exact(self):
        t = synth_table()
        r = R.residual_from_table(t, 0.50, 2.0, 0.002, 0.20)
        self.assertAlmostEqual(r["values"]["cr"],
                               10 * 0.50 + 2.0 + 1000 * 0.002 + 10 * 0.20, places=9)

    def test_linear_function_interpolated_exactly(self):
        """多线性插值对线性函数必须精确（中点也精确）。"""
        t = synth_table()
        cp, bt, v, fn = 0.60, 2.5, 0.0025, 0.25
        r = R.residual_from_table(t, cp, bt, v, fn)
        self.assertAlmostEqual(r["values"]["cr"],
                               10 * cp + bt + 1000 * v + 10 * fn, places=9)

    def test_outside_grid_clips_and_warns(self):
        """越界**不外推**（外推 = 静默编数据），只截断并警告。"""
        t = synth_table()
        r = R.residual_from_table(t, 0.90, 2.5, 0.0025, 0.25)
        self.assertTrue(any("截断" in w for w in r["warnings"]))
        self.assertAlmostEqual(r["values"]["cr"],
                               R.residual_from_table(t, 0.70, 2.5, 0.0025, 0.25)["values"]["cr"],
                               places=9)


class TestTaylorSourceAxisStrict(unittest.TestCase):
    @staticmethod
    def source_axis_table(missing_index=None):
        cps = [0.5, 0.6]
        bts = [2.0, 3.0]
        volumes = [1.0 / 10.0**3, 1.0 / 5.0**3]
        fns = [0.2, 0.3]
        grid = []
        for cp_index, _cp in enumerate(cps):
            cp_rows = []
            for bt_index, _bt in enumerate(bts):
                bt_rows = []
                for volume_index, _volume in enumerate(volumes):
                    fn_rows = []
                    for fn_index, _fn in enumerate(fns):
                        index = (cp_index, bt_index, volume_index, fn_index)
                        fn_rows.append(None if index == missing_index else (10.0 if volume_index == 0 else 20.0))
                    bt_rows.append(fn_rows)
                cp_rows.append(bt_rows)
            grid.append(cp_rows)
        return {
            "axes": {"cp": cps, "bt": bts, "volumetric": volumes, "fn": fns},
            "cr": grid,
            "scale": 0.001,
            "interpolation_coordinate": "l_over_volume_cuberoot",
            "source_axes": {"l_over_volume_cuberoot": [10.0, 5.0]},
            "source": "synthetic source-axis test",
        }

    def test_source_axis_midpoint_uses_printed_coordinate(self):
        """Catch interpolation in reciprocal-cube coordinates under a source label."""
        table = self.source_axis_table()
        volume_ratio = 1.0 / 7.5**3
        strict = R.residual_from_table(
            table, 0.5, 2.0, volume_ratio, 0.2, method="taylor_gertler_source_axis_strict"
        )
        legacy = R.residual_from_table(
            table, 0.5, 2.0, volume_ratio, 0.2, method="legacy_volume_ratio_clip_renormalize"
        )
        self.assertTrue(math.isclose(strict["values"]["cr"], 0.015, rel_tol=1e-10))
        self.assertNotEqual(strict["values"]["cr"], legacy["values"]["cr"])
        self.assertEqual(strict["method"], "taylor_gertler_source_axis_strict")
        self.assertEqual(strict["interpolation_coordinate"], "l_over_volume_cuberoot")

    def test_strict_missing_positive_weight_corner_is_unavailable(self):
        """Catch source-conformance renormalization across a missing table corner."""
        table = self.source_axis_table(missing_index=(1, 1, 1, 1))
        result = R.residual_from_table(
            table,
            0.55,
            2.5,
            1.0 / 7.5**3,
            0.25,
            method="taylor_gertler_source_axis_strict",
        )
        self.assertIsNone(result["values"]["cr"])
        self.assertFalse(result["complete"])
        self.assertTrue(any(d["code"] == "taylor.missing_corner" for d in result["diagnostics"]))

    def test_exact_node_ignores_unrelated_zero_weight_holes(self):
        """Catch requiring cells that do not contribute to an exact-node request."""
        table = self.source_axis_table(missing_index=(1, 1, 1, 1))
        result = R.residual_from_table(
            table,
            0.5,
            2.0,
            1.0 / 10.0**3,
            0.2,
            method="taylor_gertler_source_axis_strict",
        )
        self.assertEqual(result["values"]["cr"], 0.01)
        self.assertTrue(result["complete"])

    def test_strict_outside_domain_and_undeclared_axis_are_unavailable(self):
        """Catch endpoint clipping or silent reinterpretation in strict mode."""
        table = self.source_axis_table()
        outside = R.residual_from_table(
            table, 0.7, 2.0, 1.0 / 7.5**3, 0.2, method="taylor_gertler_source_axis_strict"
        )
        self.assertIsNone(outside["values"]["cr"])
        self.assertTrue(any(d["code"] == "taylor.outside_table" for d in outside["diagnostics"]))
        del table["interpolation_coordinate"]
        with self.assertRaises(ValueError):
            R.residual_from_table(
                table, 0.5, 2.0, 1.0 / 7.5**3, 0.2, method="taylor_gertler_source_axis_strict"
            )

    def test_strict_mode_rejects_reconstructed_source_headings(self):
        """Catch presenting reciprocal-cube reconstruction as a declared source axis."""
        table = self.source_axis_table()
        del table["source_axes"]
        with self.assertRaisesRegex(ValueError, "source_axes"):
            R.residual_from_table(
                table,
                0.5,
                2.0,
                1.0 / 7.5**3,
                0.2,
                method="taylor_gertler_source_axis_strict",
            )
        table = self.source_axis_table()
        table["source_axes"]["l_over_volume_cuberoot"][0] = 10.1
        with self.assertRaisesRegex(ValueError, "stored node 0"):
            R.residual_from_table(
                table,
                0.5,
                2.0,
                1.0 / 7.5**3,
                0.2,
                method="taylor_gertler_source_axis_strict",
            )

    def test_source_headings_map_to_stored_axis(self):
        """Catch reversing headings without reversing their associated cells."""
        for heading in (5.5, 6.0, 7.0, 8.0, 9.0, 10.0):
            self.assertTrue(
                math.isclose(R.taylor_volume_ratio(heading), 1.0 / heading**3, rel_tol=1e-10)
            )

    def test_tracked_table_adapter_uses_exact_headings_without_rewriting_cells(self):
        """Catch using rounded reciprocal nodes as the strict interpolation coordinate."""
        raw = cr_table_case()
        adapted = R.taylor_gertler_source_table(raw)
        self.assertEqual(
            adapted["source_axes"]["l_over_volume_cuberoot"],
            [10.0, 9.0, 8.0, 7.0, 6.0, 5.5],
        )
        self.assertEqual(
            adapted["source_axis_mapping"]["compatibility_axis_policy"],
            "rounded_reciprocal_cube_9_decimal_places",
        )
        self.assertEqual(adapted["source_axis_mapping"]["decimal_places"], 9)
        self.assertIn("associated by index", adapted["source_axis_mapping"]["source_note"])
        self.assertEqual(adapted["cr"], raw["cr"])
        source_midpoint = 9.5
        result = R.residual_from_table(
            adapted,
            0.6,
            2.25,
            R.taylor_volume_ratio(source_midpoint),
            0.16,
            method="taylor_gertler_source_axis_strict",
        )
        self.assertEqual(result["source_axis_mapping"], adapted["source_axis_mapping"])
        expected = 0.5 * (raw["cr"][1][0][0][0] + raw["cr"][1][0][1][0]) * raw["scale"]
        self.assertTrue(math.isclose(result["values"]["cr"], expected, rel_tol=1e-10,
                                     abs_tol=1e-10))

    def test_source_heading_association_uses_fixed_algebraic_tolerance(self):
        """Catch accepting node disagreement above the declared 1e-10 tolerance."""
        raw = cr_table_case()
        headings = [10.0, 9.0, 8.0, 7.0, 6.0, 5.5]
        headings[0] = (raw["axes"]["volumetric"][0] + 2e-10) ** (-1.0 / 3.0)
        with self.assertRaisesRegex(ValueError, "stored node 0"):
            R.taylor_gertler_source_table(raw, headings)

    def test_strict_speed_curve_does_not_clip_outside_froude(self):
        """Catch compatibility clipping leaking into strict source mode."""
        table = R.taylor_gertler_source_table(cr_table_case())
        hull = {"lwl_m": 100.0, "s_m2": 2000.0, "cp": 0.6, "bt": 3.0,
                "volumetric": R.taylor_volume_ratio(8.0), "estimate": True}
        curve = R.speed_power_curve(
            hull,
            [1.0],
            table,
            interpolation_method="taylor_gertler_source_axis_strict",
            friction_method="schoenherr_implicit_ittc_0.242",
            speed_conversion_method="international_knot_exact",
        )
        row = curve["rows"][0]
        self.assertFalse(row["complete"])
        self.assertIsNone(row["rt_kN"])
        self.assertEqual(row["fr"], row["fr_used"])
        self.assertEqual(curve["methods"]["interpolation"], "taylor_gertler_source_axis_strict")
        self.assertEqual(curve["methods"]["friction"], "schoenherr_implicit_ittc_0.242")
        self.assertEqual(curve["methods"]["speed_conversion"], "international_knot_exact")
        self.assertEqual(row["source_axis_mapping"], table["source_axis_mapping"])
        self.assertTrue(math.isclose(row["rn"], (1852.0 / 3600.0) * 100.0 / R.NU_SEA_15C,
                                     rel_tol=1e-10))

    def test_strict_curve_preserves_structured_table_diagnostic_and_speed_context(self):
        """Catch reducing a blocking missing-corner result to an unstructured warning."""
        table = self.source_axis_table(missing_index=(1, 1, 1, 1))
        hull = {
            "lwl_m": 100.0,
            "s_m2": 2000.0,
            "cp": 0.55,
            "bt": 2.5,
            "volumetric": R.taylor_volume_ratio(7.5),
            "estimate": True,
        }
        speed_kn = 0.25 * math.sqrt(9.81 * 100.0) / R.KNOT_MPS_EXACT
        curve = R.speed_power_curve(
            hull,
            [speed_kn],
            table,
            interpolation_method="taylor_gertler_source_axis_strict",
            speed_conversion_method="international_knot_exact",
        )
        diagnostic = curve["diagnostics"][0]
        self.assertEqual(diagnostic["code"], "taylor.missing_corner")
        self.assertEqual(diagnostic["path"], "$.speeds_kn[0]")
        self.assertEqual(diagnostic["speed_kn"], speed_kn)
        self.assertEqual(curve["rows"][0]["diagnostics"], [diagnostic])


class TestPowerAndBacksolve(unittest.TestCase):
    def test_effective_power_exact(self):
        r = R.effective_power(1_000_000.0, 10.0)
        self.assertAlmostEqual(r["values"]["pe_kw"], 10000.0, places=9)
        self.assertAlmostEqual(r["values"]["pe_shp"], 10000.0 / R.HP_TO_KW, places=6)

    def test_residual_force_definition(self):
        rr = R.residual_force(0.002, 10.0, 2000.0)
        self.assertAlmostEqual(rr["values"]["rr_n"],
                               0.5 * R.RHO_SEA * 2000.0 * 0.002 * 100.0, places=6)

    def test_backsolve_arithmetic(self):
        """SHP 10000 @ 20 kn、QPC 0.5、Rf 已知 → R_total = P/V，Rr = R_total − Rf。"""
        v_kn = 20.0
        v = v_kn * R.KNOT_MPS
        pe_w = 10000.0 * R.HP_TO_KW * 1000.0 * 0.5
        rf = 300_000.0
        r = R.implied_residual_from_trial(10000.0, v_kn, rf, 2000.0, qpc=0.5)
        self.assertAlmostEqual(r["values"]["pe_kw"], pe_w / 1000.0, places=6)
        self.assertAlmostEqual(r["values"]["r_total_n"], pe_w / v, places=3)
        self.assertAlmostEqual(r["values"]["rr_n"], pe_w / v - rf, places=3)

    def test_qpc_assumption_is_flagged(self):
        r = R.implied_residual_from_trial(83000.0, 28.1, 1.2e6, 6407.9, qpc=0.55)
        self.assertTrue(any("QPC" in w and "无来源" in w for w in r["warnings"]))


def cr_table_case():
    p = os.path.join(PKG, "cases", "taylor_gertler_cr_table.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class TestCrTableIntegrity(unittest.TestCase):
    """Taylor-Gertler 表（Molland A3.8–A3.11）：结构与书中抽检值。"""

    @classmethod
    def setUpClass(cls):
        cls.case = cr_table_case()

    def test_shape_and_axes(self):
        ax = self.case["axes"]
        self.assertEqual(ax["cp"], [0.5, 0.6, 0.7, 0.8])
        self.assertEqual(ax["bt"], [2.25, 3.0, 3.75])
        self.assertEqual(len(ax["volumetric"]), 6)      # L/∇⅓ = 10,9,8,7,6,5.5
        self.assertEqual(len(ax["fn"]), 22)             # Fr 0.16–0.58 步长 0.02
        g = self.case["cr"]
        self.assertEqual((len(g), len(g[0]), len(g[0][0]), len(g[0][0][0])),
                         (4, 3, 6, 22))

    def test_scale_is_thousandth(self):
        """表内是 CR×1000，scale 必须为 1e-3（否则 Cr 差一千倍）。"""
        self.assertEqual(self.case["scale"], 1e-3)

    def test_book_spot_rows(self):
        """书中抽检（已与原书页面逐格核对）：
        Cp=0.60 Fr=0.16 全 18 值；Cp=0.50 Fr=0.40 前 9 格缺。"""
        r60 = self.case["raw_rows"]["0.60"]["0.16"]
        self.assertEqual(r60, [0.50, 0.60, 0.75, 0.42, 0.51, 0.65, 0.35, 0.42, 0.51,
                               0.29, 0.38, 0.48, 0.22, 0.32, 0.44, 0.23, 0.30, 0.42])
        r50 = self.case["raw_rows"]["0.50"]["0.40"]
        self.assertEqual(r50[:9], [None] * 9)
        self.assertEqual(r50[9:], [3.71, 3.80, 3.95, 2.58, 2.63, 2.64, 1.75, 1.82, 1.90])

    def test_cp_080_isolated_holes_are_genuine(self):
        """Cp=0.80 Fr=0.30 的孤立缺格已与原书页面核对，是原书真实的「—」。"""
        self.assertEqual(self.case["raw_rows"]["0.80"]["0.30"],
                         [None] * 6 + [5.20, None, None, 3.70, 4.00, 3.87,
                                       2.77, None, None, 2.20, None, None])


class TestInterpolationWithHoles(unittest.TestCase):
    def test_missing_corners_renormalised(self):
        """缺格 → 按可用角点重新归一化 + 警告，**不当 0 也不崩**。"""
        t = {"axes": {"cp": [0.5, 0.6], "bt": [2.0, 3.0], "volumetric": [0.002, 0.003],
                      "fn": [0.2, 0.3]},
             "cr": [[[[1.0, None], [None, 2.0]], [[3.0, 3.0], [3.0, 3.0]]],
                    [[[5.0, 5.0], [5.0, 5.0]], [[5.0, 5.0], [5.0, 5.0]]]]}
        r = R.residual_from_table(t, 0.55, 2.5, 0.0025, 0.25)
        self.assertIsNotNone(r["values"]["cr"])
        self.assertTrue(any("缺格" in w for w in r["warnings"]))

    def test_all_corners_missing_gives_none(self):
        t = {"axes": {"cp": [0.5, 0.6], "bt": [2.0, 3.0], "volumetric": [0.002, 0.003],
                      "fn": [0.2, 0.3]},
             "cr": [[[[None, None], [None, None]], [[None, None], [None, None]]],
                    [[[None, None], [None, None]], [[None, None], [None, None]]]]}
        r = R.residual_from_table(t, 0.55, 2.5, 0.0025, 0.25)
        self.assertIsNone(r["values"]["cr"])


if __name__ == "__main__":
    unittest.main()
