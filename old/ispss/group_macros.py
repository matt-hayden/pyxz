from spss import SetMacroValue
from spssaux import VariableDict

for vlevel in ["nominal", "ordinal", "scale", "unknown"]:
	name = "!{}s".format(vlevel)
	vd = VariableDict(variableLevel=[vlevel])
	SetMacroValue(name, " ".join(str(_) for _ in vd))

vl = [ _ for _ in VariableDict() if _.Attributes.pop("units","") ]
vl.sort(key = lambda _:_.Attributes["units"])
for units, vg in groupby(vl, key = lambda _:_.Attributes["units"]):
	name = "!{}_quantities".format("_".join(units.replace("/","per").split()))
	print units, name
	SetMacroValue(name, " ".join(str(_) for _ in vg))