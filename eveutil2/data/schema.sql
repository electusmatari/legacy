CREATE TABLE grd_journal (
    id bigserial NOT NULL,
    account integer NOT NULL,
    date timestamp without time zone NOT NULL,
    refid bigint NOT NULL,
    reftypeid integer NOT NULL,
    ownername1 character varying(255) NOT NULL,
    ownerid1 integer NOT NULL,
    ownername2 character varying(255) NOT NULL,
    ownerid2 integer NOT NULL,
    argname1 character varying(255) NOT NULL,
    argid1 integer NOT NULL,
    amount double precision NOT NULL,
    balance double precision NOT NULL,
    reason character varying(255) NOT NULL,
    taxreceiverid bigint,
    taxamount double precision
);

CREATE INDEX grd_journal_account_idx ON grd_journal USING btree (account);
CREATE INDEX grd_journal_date_idx ON grd_journal USING btree (date);
CREATE INDEX grd_journal_refid_idx ON grd_journal USING btree (refid);

CREATE TABLE grd_transactions (
    id bigserial NOT NULL,
    account integer NOT NULL,
    date timestamp without time zone NOT NULL,
    transactionid bigint NOT NULL,
    quantity integer NOT NULL,
    typename character varying(255) NOT NULL,
    typeid integer NOT NULL,
    price double precision NOT NULL,
    clientid integer NOT NULL,
    clientname character varying(255) NOT NULL,
    characterid integer NOT NULL,
    charactername character varying(255) NOT NULL,
    stationid integer NOT NULL,
    stationname character varying(255) NOT NULL,
    transactiontype character varying(255) NOT NULL,
    transactionfor character varying(255) NOT NULL
);

CREATE INDEX grd_transactions_account_idx ON grd_transactions USING btree (account);
CREATE INDEX grd_transactions_date_idx ON grd_transactions USING btree (date);
CREATE INDEX grd_transactions_transactionid_idx ON grd_transactions USING btree (transactionid);
