#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" core.py

Main class for passages
"""
__author__ = 'Scott Burns <scott.s.burns@vanderbilt.edu>'
__copyright__ = 'Copyright 2012 Vanderbilt University. All Rights Reserved'

from .metadata import CORRECT, MANIP


class PassageRunner(object):

    def __init__(self, ident, group, series):
        self.id = ident
        self.grp = group
        self.ser = series

    def process(self):
        all_passages = ('toads', 'sap', 'oct', 'scabs', 'mustangs',
                        'hab', 'moths', 'wbf', 'crocs', 'igloos',
                        'bugs', 'deserts')
        results = {}
        for ptype in all_passages:
            corr_trials = [(i, p[0], p[1], p[2]) for i, p in enumerate(CORRECT) if p[0] == ptype]
            results[ptype] = {}
            for ind, ptype, qtype, corr in corr_trials:
                if qtype not in results[ptype].keys():
                    results[ptype][qtype] = {'raw': 0, 'tot': 0}
                results[ptype][qtype]['tot'] += 1
                # oct questions in the redcap survery are 'octo'
                if ptype == 'oct':
                    word_pass = 'octo'
                else:
                    word_pass = ptype
                word_key = '%s_q%d' % (word_pass, (ind + 1))
                sub_answer = self.ser[word_key]
                if sub_answer == corr:
                    results[ptype][qtype]['raw'] += 1
            all_corr = 0
            all_tot = 0
            for q in results[ptype].keys():
                tot = results[ptype][q]['tot']
                cor = results[ptype][q]['raw']
                results[ptype][q]['percent'] = ((float(cor) / tot) * 100)
                all_tot += tot
                all_corr += cor
            results[ptype]['total_correct'] = {'raw': all_corr, 'percent': (float(all_corr) / all_tot * 100)}
        self.results = results
        # Add summary
        self.results['summary'] = {}
        for man, manstr in zip(('v', 's', 'd', 'c'), ('vocab', 'syntax', 'decoding', 'cohesion')):
            #  Find which passage was this manip
            pas = [k for k, v in MANIP[self.grp].items() if v == man][0]
            for qtype, qdata in self.results[pas].items():
                new_key = '_'.join([manstr, qtype, 'percent'])
                self.results['summary'][new_key] = qdata['percent']
        # Now lets do all qtype
        for qtype, qtot in zip(('compmon', 'interpretation', 'critical_analysis', 'factual', 'process_strategy', 'total_correct'), (12, 36, 9, 35, 16, 108)):
            sum_corr = sum([pdata[qtype]['raw'] for ptype, pdata in self.results.items() if ptype != 'summary' and qtype in pdata])
            corr_key = '_'.join(['summary', qtype, 'raw'])
            self.results['summary'][corr_key] = sum_corr
            pct_key = '_'.join(['summary', qtype, 'percent'])
            self.results['summary'][pct_key] = float(sum_corr) / qtot * 100

    def convert_to_redcap(self):
        data = {'participant_id': self.id}
        for ptype, pdata in self.results.items():
            if ptype != 'summary':
                manip_k = MANIP[self.grp][ptype] if ptype in MANIP[self.grp] else 'b'
                for qtype, qdata in pdata.items():
                    for key, fmt in zip(('raw', 'percent'), ('%d', '%0.3f')):
                        if ptype in ('deserts', 'toads'):
                            new_key = '_'.join([ptype, qtype, key])
                        else:
                            new_key = '_'.join([ptype, manip_k, qtype, key])
                        data[new_key] = fmt % qdata[key]
            else:
                # We just need to fmt all k/v in pdata
                for key, v in pdata.items():
                    fmt = '%d' if 'raw' in key else '%0.3f'
                    data[key] = fmt % v
        #  Fill in complete
        data['questions_summary_complete'] = '2'
        data['questions_complete'] = '2'
        return data
