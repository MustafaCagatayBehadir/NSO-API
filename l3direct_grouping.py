import pandas as pd


def main(base_file, reference_file):
    group_list = []
    df_base = pd.read_excel(base_file, sheet_name="L3DIRECT")
    df_refer = pd.read_excel(reference_file, sheet_name="GRUP SIRA")
    df_refer = df_refer.astype({"GRUP": int})
    for index_refer in df_refer.index.values:
        tenant_name_refer = df_refer.loc[index_refer]["TENANT NAME"]
        service_name_refer = df_refer.loc[index_refer]["SERVICE NAME"]
        if df_refer.loc[index_refer]["GRUP"] not in group_list:
            group_list.append(df_refer.loc[index_refer]["GRUP"])
        for index_base in df_base.index.values:
            tenant_name_base = df_base.loc[index_base]["TENANT NAME"]
            service_name_base = df_base.loc[index_base]["SERVICE NAME"]
            if tenant_name_base == tenant_name_refer and service_name_base == service_name_refer:
                df_base.loc[index_base, "GRUP"] = df_refer.loc[index_refer]["GRUP"]
    df_base["GRUP"].fillna(0, inplace=True)
    output = ""
    for grup in group_list:
        grup_tenant_list = []
        for index in df_base.index.values:
            if grup == df_base.loc[index]["GRUP"]:
                grup_tenant_list.append(df_base.loc[index]["TENANT NAME"])
                if df_base.loc[index]["TENANT NAME"] not in grup_tenant_list:
                    grup_tenant_list.append(df_base.loc[index]["TENANT NAME"])
        line = f"Group: {grup} Tenant List: {','.join(str(x) for x in grup_tenant_list)}\n"
        output += line
        output += len(line)*"*" + "\n"
    with pd.ExcelWriter("L3DIRECT_GROUPS.xlsx") as writer:
        df_base.to_excel(writer, index=False)
    with open("L3DIRECT_GROUPS_TENANT_LIST.txt", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main(base_file="Gebze SOL1_services_limited_OFC_v2.xlsx", reference_file="Gebze SOL1_services_limited_OFC_v2_L3GRUP.xlsx")
