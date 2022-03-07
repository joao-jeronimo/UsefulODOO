#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import io, time, datetime, odoolib, tempfile, re, base64
import traceback
from . import OdooCommException

import pdb

DEFAULT_BATCH_SIZE = 300

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:min(i+n, len(lst))]

class ChartOfAccounts:
    def __init__(self, connection, company_id, default_account_name="Sem nome", include_generic_accounts=True, extra_cols=[]):
        self.connection = connection
        self.company_id = company_id
        self.account_model = self.connection.get_model("account.account")
        self.default_account_name = default_account_name
        self.include_generic_accounts = include_generic_accounts
        self.batch_size = DEFAULT_BATCH_SIZE
        self._accounts_cols.extend(extra_cols)
    def __enter__(self):
        # Export out all accounts:
        self._all_accounts_ids = self.account_model.search([
                    ('company_id', '=', self.company_id),
                    ], context={'include_generic_accounts': self.include_generic_accounts})
        _all_accounts = self.account_model.export_data(self._all_accounts_ids, self._accounts_cols, context=self.orm_acc_context)['datas']
        # Make sure all non-strign elemnts of the account are converted to string (otherwise, e.g. booleans will not reimport later):
        _all_accounts = list(map(lambda ll: list(map(lambda mm: str(mm), ll)), _all_accounts))
        self._all_accounts = _all_accounts
        return self
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            exit(-1)
        accounts_to_commit = tuple(filter(lambda a: a[self._accounts_cols.index('code')] in self._modified_accounts, self._all_accounts))
        print("Loading all accounts (total %d accounts to commit)..."%len(accounts_to_commit))
        for accounts_chunk in chunks(accounts_to_commit, self.batch_size):
            print(" ... loading batch of %d accounts ..."%len(accounts_chunk))
            loadret = self.account_model.load(self._accounts_cols, accounts_chunk, context=self.orm_acc_context)
            if loadret['ids'] == False:
                print("============= ERRO! =============")
                print("loadret = "+str(loadret))
                #pdb.set_trace()
                exit(-1)
    
    _accounts_cols = ["id", "code", "name", "user_type_id/id", "reconcile", ]
    orm_acc_context = {'level_types': 'all'}
    _modified_accounts = []
    
    def _apply_dikt_to_account(self, account_as_list, dikt):
        self._modified_accounts.append(account_as_list[self._accounts_cols.index('code')])
        if 'code' in dikt.keys():
            self._modified_accounts.append(dikt['code'])
        for key in dikt:
            account_as_list[self._accounts_cols.index(key)] = dikt[key]
    
    def find_account(self, account_code):
        #pdb.set_trace()
        matching_accounts = list(filter(lambda acc: acc[self._accounts_cols.index("code")]==str(account_code), self._all_accounts))
        if   len(matching_accounts)==0:
            return False
        elif len(matching_accounts)==1:
            return matching_accounts[0]
        else:
            print("More than one account with code %s."%account_code)
            exit(-1)
    
    def modify_account(self, account_code, dikt={}):
        the_account = self.find_account(account_code)
        if the_account:
            self._apply_dikt_to_account(the_account, dikt=dikt)
        else:
            raise OdooCommException("Account not found in Odoo server: '%s'"%account_code)
    
    def create_or_modify_account(self, account_code, dikt={}):
        the_account = self.find_account(account_code)
        if the_account:
            self._apply_dikt_to_account(the_account, dikt=dikt)
        else:
            print("acccod%s"%(account_code), end="; ")
            new_account = [None]*len(self._accounts_cols)
            self._apply_dikt_to_account(new_account, dikt={
                'id':               None,
                'code':             account_code,
                'name':             self.default_account_name,
                'user_type_id/id':  "account_generic.account_type_generic",
                'reconcile':        str(False),
                **dikt })
            self._all_accounts.append(new_account)
