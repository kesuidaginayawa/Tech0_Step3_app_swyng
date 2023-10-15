!pip install plotly
import streamlit as st
import numpy as np
import pandas as pd
import json
import plotly.express as px
import requests
from PIL import Image
from io import BytesIO

tab1, tab2, tab3 = st.tabs(["ざっくり検索", "アンケート", "お部屋探し条件"])

with tab1:

    #<1st view>-----------------------------------------
    st.title('お部屋探しアプリ')
    image_url = "https://hellointerior.jp/images/case1_k1.jpg"# 画像のURL
    response = requests.get(image_url) # 画像をダウンロード
    image = Image.open(BytesIO(response.content)) #開く
    st.image(image) #画像表示
    st.write('アンケートに答えていくとお部屋が表示されます。')
    #---------------------------------------------------

    #<1st:アンケート>-----------------------------------
    st.subheader('①勤務先を教えてください',divider='blue')
    st.text_input('郵便番号','555-555')
    st.text_input('住所','神奈川県横浜市西区高島3-4-5')
    st.text_input('最寄り駅','横浜駅')
    #--------------------------------------------------

    #<2nd: view>--------------------------------------------
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

    if st.button('決定'):
        st.session_state.button_clicked = True

    if st.session_state.button_clicked:

        #<import>-------------------------------------------
        # 物件データ
        df = pd.read_csv('..\\FileForViz\\distinct_mean_values.csv')
        # 行政区域データ
        with open("..\\RawData\\town.geojson", encoding='utf-8') as f:
            twn = json.load(f)
        # 駅の緯度経度データ
        sttn = pd.read_csv('..\\FileForViz\\df_stations.csv')
        #---------------------------------------------------

        #<fig1>---------------------------------------------
        st.subheader('区・町村別',divider='green')
        floors = df['間取り'].unique().tolist()
        floor = st.multiselect('選んだ間取りでフィルタされます。',(floors),['1K'])
        t_df = df[df['間取り'].isin(floor)]
        col1_left, col1_right = st.columns(2)
        color_elem =  col1_left.selectbox('色が変わります',("賃料（万円）","専有面積(m^2)","件数","徒歩分数(分)"))
        hover_data = col1_right.multiselect('カーソルを合わせると情報が表示されます。',("専有面積(m^2)","賃料（万円）","件数","徒歩分数(分)"))

        st.markdown("<h4 style='color:royalblue'><u>平均{}</u></h4>".format(color_elem),unsafe_allow_html=True)
        fig1 = px.choropleth_mapbox(
            t_df,
            geojson=twn,
            locations="所在地_市区町村",
            color=color_elem,
            hover_name="所在地_市区町村",
            hover_data=hover_data,
            featureidkey="properties.N03_004",
            mapbox_style="carto-positron",
            zoom=10,
            center={"lat":35.45, "lon": 139.58},
            opacity=0.5,
            width=800,
            height=800,
        )
        fig1.update_layout(
            autosize=True,
            # width=700,  # Width in pixels
            # height=700,  # Height in pixels
        )
        st.plotly_chart(fig1, use_container_width=True)
        #--------------------------------------------------

        #<fig2>---------------------------------------------
        st.subheader('駅別',divider='green')
        floors = sttn['間取り'].unique().tolist()
        floor = st.selectbox('選んだ間取りでフィルタされます。',(floors))
        t_sttn = sttn[sttn['間取り']==floor]

        towns = t_sttn['所在地_市区町村'].unique().tolist()

        col2_left, col2_right = st.columns(2)
        town = col2_left.multiselect('気になる町',(towns),['横浜市中区'])
        col3_left, col3_right = st.columns(2)
        size = col3_left.selectbox('円のサイズが変わります',("件数","賃料（万円）","専有面積(m^2)"))
        color = col3_right.selectbox('円の色が変わります',("賃料（万円）","件数","専有面積(m^2)"))
        
        t_sttn = t_sttn[t_sttn['所在地_市区町村'].isin(town)]
        fig2 = px.scatter_mapbox(
            t_sttn, 
            lat="lat", 
            lon="lon", 
            color=color, 
            size=size,
            size_max=20, 
            zoom=10,
            mapbox_style="carto-positron",
            hover_data=["沿線", "駅"]
            )

        fig2.update_layout(
            autosize=True,
            width=700,  # Width in pixels
            height=700,  # Height in pixels
        )

        st.plotly_chart(fig2, use_container_width=True)
        #--------------------------------------------------
        st.dataframe(t_sttn)
        ppty_lst = t_sttn['駅'].unique().tolist()
        station = st.selectbox("気になる駅を選んでください",(ppty_lst))
    #------------------------------------------------------



with tab2:
    st.title('物件選択：生活条件')

    with st.form("my_form", clear_on_submit=False):

        st.subheader("忙しい朝")
        morning = st.radio("早起きは得意?",("朝活するレベル","平気","出来なくはない","苦手"),horizontal=True)
        check1 = st.checkbox("",key="imp1",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        breakfast = st.radio("朝食は毎日食べる？",options=("食べる","大体食べる","たまに食べる","食べない"),horizontal =True)
        check2 = st.checkbox("",key="imp2",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        morningTime =  st.radio("家を出るための準備、どのくらいかかる？",options=("~15分","~30分","~60分","~90分","90分~"),horizontal =True)
        check3 = st.checkbox("",key="imp3",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        senmen = st.multiselect("洗面台で何をする？",options=("洗顔","手洗い",'歯磨き',"メイク(~20分)","メイク(20分~)","スキンケア(~2種)","スキンケア(3種~)","ヘアセット","ひげ・産毛処理"))
        check4 = st.checkbox("",key="imp4",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        st.subheader("日々の生活")
        cooking = st.radio("晩御飯はどうする？",options=("毎日ご飯+3品以上","毎日ご飯+2品くらい","作れるときは作る","スーパーかコンビニで調達"),horizontal =True)
        check6 = st.checkbox("",key="imp6",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        bathtime = st.radio("お風呂の過ごし方",options = ("シャワーだけ","たまにはお風呂","毎日お風呂"),horizontal =True)
        check7 = st.checkbox("",key="imp7",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        raundry = st.radio("洗濯スタイルは？",options=("天日干し","部屋干し","浴室乾燥機","乾燥機付き洗濯機"),horizontal =True,help="室内干しは天気に左右されないのが最大メリット \n 浴室乾燥機は便利だが家賃・電気代高め \n乾燥機付き洗濯機はシワさえ気にならなければOK")
        check8 = st.checkbox("",key="imp8",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        fashion1 = st.radio("服は大体何着ぐらいもってる？(1シーズン)",options=("10着以下","20着以下","30着以下","30着より多い(又は衣替えしない)"),horizontal =True)
        check9 = st.checkbox("",key="imp9",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        fashion2 = st.radio("靴は何足もってる？",options=("4足以下","10足以下","10足より多い"),horizontal =True)
        check10 = st.checkbox("",key="imp10",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        move = st.multiselect("移動手段は？",options=("徒歩","自転車","車","公共交通機関"))
        check11 = st.checkbox("",key="imp11",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        pet = st.radio("ペットを飼う予定は？",options=("ない","ある・飼っている"),horizontal =True)
        check12 = st.checkbox("",key="imp12",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        st.subheader("プライベートタイム")
        live = st.multiselect("寝る以外で部屋ですること",options=("テレビ・モニターで何かを見る","携帯・タブレットで何かを見る","ゲーム(PC)","筋トレ・ストレッチ","人を呼ぶ","じっと集中するタイプの趣味"))
        check13 = st.checkbox("",key="imp13",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        holiday = st.radio("予定がない日の過ごし方",options=("予定がなくても予定を作って出かける","家のこと(掃除・洗濯・作り置き等)をして動き回る","SNSや動画を見て過ごす"),horizontal =True)
        check14 = st.checkbox("",key="imp14",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        ddd = st.radio("ほぼ一日中ベッドの上で生活",options=("あり","許容範囲内","なし"),horizontal =True)
        check15 = st.checkbox("",key="imp15",help="自分にとって住居選択に大きく影響しそうと感じる質問だった場合チェック")
        submitted = st.form_submit_button("submit")
indexNum = 0
select = ["横浜市鶴見区","横浜市神奈川区"]
bukkenTop3 =[]

access= pd.read_csv("..\\RawData\\access.csv")
baseInf=pd.read_csv("..\\RawData\\property.csv")

if submitted:
    if check1 == True:
        if (morning == "苦手") and ((morningTime == "~90分")or(morningTime=="90分~")):
            access = access[access["徒歩分数(分)"]<5]
            accessTop3 = access.sort_values("徒歩分数(分)").head(3)
            top3ID = accessTop3["物件CD"]
            
            for a in top3ID:
                bukken = baseInf[baseInf["物件CD"]==a]
                bukkenImage = bukken["間取り図"]
                # bukkenTop3.append(bukkenImage)
            indexNum = 1            
        elif ((morning == "苦手") and (morningTime == "~60分"))or((morning == "出来なくはない")and(morningTime == "~90分")or(morningTime=="90分~")):
            access == access[access["徒歩分数(分)"]<10]
            indexNum = 3    
        else:
            access == access
            indexNum = 6
    else:
        if (morning == "苦手") and ((morningTime == "~90分")or(morningTime=="90分~")):
            access = access[access["徒歩分数(分)"]<10]
            indexNum = 3  
        elif ((morning == "苦手") and (morningTime == "~60分"))or((morning == "出来なくはない")and(morningTime == "~90分")or(morningTime=="90分~")):
            access == access[access["徒歩分数(分)"]<15]
            indexNum = 4 
        else:
            access == access
            indexNum = 6



with tab3:
    with st.form("my_form2", clear_on_submit=False):
        st.title('物件選択条件')
        list = ["横浜市鶴見区","横浜市中区","横浜市磯子区","横浜市戸塚区","横浜市泉区","横浜市神奈川区","横浜市南区","横浜市金沢区","横浜市港南区","横浜市瀬谷区","横浜脚青葉区"]
        st.subheader("地域")
        selectArea = st.multiselect("地域選択で選んだ地域",(list),default=select)  
        toho = st.radio("最寄り駅までの距離(分)",options=("1分以内","5分以内","7分以内","10分以内","15分以内","20分以内","指定しない"),index=indexNum,horizontal=True)
        submitted2 = st.form_submit_button("submit2")
        # st.image(bukkenTop3[1])
        # st.table(access)
