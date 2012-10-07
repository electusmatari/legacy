#!/usr/bin/env python

import os
import sys
import urllib
import xml.etree.ElementTree as ET

import evelib.eveapi as eveapi

def main():
    (_, userid, apikey) = sys.argv
    try:
        os.mkdir(userid)
    except OSError:
        pass
    os.chdir(userid)
    api = API(userid, apikey)
    chars = api.call("/account/Characters.xml.aspx")
    for char in chars.characters:
        api.characterID = char.characterID
        try:
            os.mkdir(char.name)
        except OSError:
            pass
        os.chdir(char.name)
        api.call("/char/AccountBalance.xml.aspx")
        api.call("/char/AssetList.xml.aspx")
        api.call("/char/CharacterSheet.xml.aspx")
        api.call("/char/ContactList.xml.aspx")
        api.call("/char/IndustryJobs.xml.aspx")
        api.call("/char/MailingLists.xml.aspx")
        mails = api.call("/char/MailMessages.xml.aspx")
        if mails is not None:
            api.call("/char/MailBodies.xml.aspx",
                     ids=",".join([str(mail.messageID)
                                   for mail in mails.messages]))
        api.call("/char/MarketOrders.xml.aspx")
        api.call("/char/Medals.xml.aspx")
        api.call("/char/Research.xml.aspx")
        journal = api.call("/char/WalletJournal.xml.aspx")
        if journal is None:
            done = True
        else:
            done = False
        while not done:
            if not hasattr(journal, 'entries') or len(journal.entries) == 0:
                break
            beforeRefID = min([entry.refID for entry in journal.entries])
            journal = api.call("/char/WalletJournal.xml.aspx",
                               beforeRefID=beforeRefID)
            if journal is None:
                done = True
        transactions = api.call("/char/WalletTransactions.xml.aspx")
        if transactions is None:
            done = True
        else:
            done = False
        while not done:
            if not hasattr(transactions, 'transactions') or len(transactions.transactions) == 0:
                break
            beforeTransID = min([entry.transactionID
                                 for entry in transactions.transactions])
            transactions = api.call("/char/WalletTransactions.xml.aspx",
                                    beforeTransID=beforeTransID)
            if transactions is None:
                done = True
        os.chdir("..")
    
class API(object):
    def __init__(self, keyID=None, vCode=None, characterID=None):
        self.keyID = keyID
        self.vCode = vCode
        self.characterID = characterID

    def args(self):
        result = []
        if self.keyID is not None:
            result.append(("keyID", self.keyID))
        if self.vCode is not None:
            result.append(("vCode", self.vCode))
        if self.characterID is not None:
            result.append(("characterID", self.characterID))
        return result

    def call(self, path, **kwargs):
        fobj = urllib.urlopen("http://api.eveonline.com%s?%s" % 
                              (path,
                               urllib.urlencode(self.args() + kwargs.items())))
        xmldata = fobj.read()
        simpleurl = ("http://api.eveonline.com%s?%s" %
                     (path, urllib.urlencode(kwargs.items()),))
        fname = simpleurl.replace("/", "_")
        try:
            result = eveapi.ParseXML(xmldata)
        except eveapi.Error:
            sys.stderr.write("No permission for API call %s\n" %
                             (simpleurl,))
            return None
        if len(fname) > 255:
            fname = fname[0:255]
        file(fname, "w").write(xmldata)
        return result

main()
