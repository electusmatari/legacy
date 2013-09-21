grd = APIKey.objects.get(name="Gradient").corp()
gms = grd.MemberSecurity()
gmt = grd.MemberTracking()
prospects = [m.name for m in gms.members
             if "Prospect" in [t.titleName for t in m.titles]]
non_prospects = [m.name for m in gms.members
                 if "Prospect" not in [t.titleName for t in m.titles]]
everyone = [m.name for m in gms.members]

c.execute("UPDATE vote SET allowed_voters = %s WHERE id IN (163, 164)",
          ["".join((name + "\n") for name in non_prospects)])
for name in everyone:
    c.execute("INSERT INTO vote_option (vote_id, name) "
              "VALUES (%s, %s)",
              [163, name])

from emtools.ccpeve.models import apiroot
api = apiroot()

old = time.time() - (60*60*24*365*2)

younger_than_two_years = []
for m in gmt.members:
    cs = api.eve.CharacterInfo(characterID=m.characterID)
    license = cs.employmentHistory[-1].startDate
    if license > old:
        younger_than_two_years.append(m.name)


for name in younger_than_two_years:
    c.execute("INSERT INTO vote_option (vote_id, name) "
              "VALUES (%s, %s)",
              [164, name])
