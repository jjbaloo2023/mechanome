"""Render the accepted-observable candidates from immutable passive-area states."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'research' / '.mpl-passive-area'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np

records = json.loads((ROOT / 'research/passive_area_results_001.json').read_text(encoding='utf-8'))['records']
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
figure, axes = plt.subplots(1, 2, figsize=(11, 5))
colors = ['#aecbe0', '#6d9fbf', '#347797', '#154c68']
for amplitude, color in zip((.02, .1, .3, .6), colors):
    rows = sorted([row for row in records if row['case']['c_repo_ell'] == amplitude], key=lambda row: row['case']['x'])
    area = [row['observables']['material_coat_area_over_2pi_ell2'] for row in rows]
    apex = [row['observables']['apex_H_over_C_source'] for row in rows]
    axes[0].plot(area, apex, marker='o', color=color, label=f'c ell = {amplitude:g}')
axes[0].set(xscale='log', xlabel='Nominal material coat area / (2 pi ell²)',
            ylabel='Apex mean curvature / C source', title='A  Sampled area ordering')
axes[0].set_xticks([.125, .5, 2], labels=['0.125', '0.5', '2'])
axes[0].xaxis.set_minor_formatter(NullFormatter())
axes[0].legend(frameon=False, loc='lower left', fontsize=9)
strong = sorted([row for row in records if row['case']['c_repo_ell'] == .6], key=lambda row: row['case']['x'])
locations = np.arange(3)
axes[1].bar(locations-.18, [row['observables']['apex_H_over_C_source'] for row in strong],
            width=.36, color='#154c68', label='Pointwise apex')
axes[1].bar(locations+.18, [row['observables']['coat_mean_H_over_C_source'] for row in strong],
            width=.36, color='#cc8246', label='Nominal coat-area mean')
axes[1].set(xticks=locations, xticklabels=['0.125', '0.5', '2'],
            xlabel='Nominal material coat area / (2 pi ell²)', ylabel='Mean curvature / C source',
            title='B  Observable definition matters (c ell = 0.6)', ylim=(0,1))
axes[1].legend(frameon=False, loc='upper right', fontsize=9)
for axis in axes:
    axis.grid(axis='y', alpha=.15)
    axis.set_axisbelow(True)
figure.suptitle('Passive membrane: saved forward solutions', fontsize=14)
figure.subplots_adjust(left=.075, right=.985, bottom=.27, top=.82, wspace=.28)
figure.text(.5,.035,'12 sampled states; maximum slope angle 0.268 rad. No global monotonicity, stability or biological claim.\nPointwise and area-averaged curvature are mathematical observables; neither is an experimental cap fit.',
            ha='center', va='bottom', fontsize=9, color='#555555')
figure.savefig(ROOT / 'research/passive_area_comparison.png', dpi=170)
