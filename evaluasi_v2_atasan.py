# library and file 
import pandas as pd 
import numpy as np
import sqlalchemy as sqla
from datetime import timedelta, datetime

# for file 
import openpyxl
import gspread

# for anythibg 
import time 
import random 
import warnings
import pytz
warnings.filterwarnings('ignore')


# streamlit moment 

import streamlit as st 

### LIBRARY MOMENT END ### 



###########################
##### GET DATA GSHEET MOMENT  #####
############################

# get from sheet data input auto
# make a cache for efficieny 

# data input
def get_data():
    data = pd.read_csv(r"https://docs.google.com/spreadsheets/d/e/2PACX-1vRXwzVHhY4kZ9kfcgSleJN2gugToAF7bU5J4YfYp9y1mRICQcxVK07j6s0wFc_XgRZ4C0rWolQWyLYL/pub?gid=528915107&single=true&output=csv")
    
    #data.drop([0,1],axis = 0,inplace = True)   
    data = data.loc[data['Tipe Penilai'] != 'Atasan'] # filter atasan di hide aja
    data['Level'] = data['Level'].str.title()     
    
    data['NIK Penilai'] = data['NIK Penilai'].fillna(0).astype('str')
    data['NIK Penilai'] = data['NIK Penilai'].str.split('.', expand = True)[0]
    
    data['Tipe Penilai'] = data['Tipe Penilai'].str.replace('-', ' ').str.title()
    data['Penilai'] = '*' + data['Nama Penilai'] + '* nik *' + data['NIK Penilai'] + '*'
    
    data['Nama Karyawan Yang Dinilai'] = '*' + data['Nama Karyawan'] + "* sebagai *" + data['Posisi'] + '* level *' + data['Level'] + '* dari' + ' Division *' + data['Divisi'] +  '* dan Hubungan nya *' + data['Tipe Penilai'] + '*'
    
    return data

# data respon hanya untuk atasan
def get_data_latest():
    data = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQLLcjSqGEpJqEkZCQSpbAB770THjfe7f6VIC6ucuHIfQjVe2sNnt08cqp4dDdEipYgaODEb_7GKdpa/pub?gid=0&single=true&output=csv')    
    data = data.drop(['Jabatan', 'Level', 'Divisi', 'Hubungan', 'Detail'], axis = 1)  
    data = data[data['Tanggung Jawab Pribadi'].isin(['1', '2', '3', '4', '5'])]
    return data


# get data moment end 



###########################
##### HEADER MOMENT #####
############################

## FOR PAGE 
st.set_page_config(
    page_title="Evaluator Kompetensi",
    page_icon="🌟",layout ='wide',
)

# ambil data 
data = get_data()

data_latest = get_data_latest()

## page 
c30, c31, c32 = st.columns([20, 1, 3])

## headder 
with c30:
    #st.image("logo.png", width=400)
    st.title("Evaluator Kompetisi Mega Perintis")
    st.header("")

## about 
# about this app 
with st.expander("ℹ️ - tentang web app ini", expanded=True):
     st.write(
        """     
-   *Evaluator Kompetisi Mega Perintis v.1.2* adalah sebuah web application penilaian untuk karyawan Mega Perintis.
	    """
    )
st.markdown("")



###########################
##### FORM PAGE MOMENT  #####
############################


save_data = {} # to dataframe


c1, c2 = st.columns([1.5, 3]) # for vertical form 
c77, c78 = st.columns([1.5, 3]) # for vertical form 



###########################
##### FORM 1 / NAMA PENILAI MOMENT  #####
############################

with c1:
    with st.form('form_1'):
        
        # nama evaluator moment 
        st.header('1. Nama Penilai')
        search_1 = st.selectbox('Cari nama penilai di sini ya!', 
                                list(data['Nama Penilai'].unique()),
                                help = 'Nama penilai disini ya')
        st.caption('Nama harus sesuai')
        
        
        #cek apakah benar si penilai nya 
        def cek_nik_penilai(nama):
            data_nama = {k: list(v) for k, v in data.groupby('NIK Penilai')['Nama Penilai']}
            if nama in data_nama.keys():
                return data_nama[nama][0]
            else:
                return 'None'
           
        
        ## input nik penilai 
        nik_eval = st.text_input('Masukan NIK Penilai', help = 'Nik penilai disini ya')
        
        korek_nik = cek_nik_penilai(nik_eval) # cek nik nya 
        
        
        #make logic function 
        def nama_yang_dinilai(nama):
            data_nama = {k: list(v) for k, v in data.groupby('Nama Penilai')['Nama Karyawan Yang Dinilai']}
            if nama in data_nama.keys():
                return data_nama[nama]
            else:
                return 'None'
            
        ## logika form 1
        b1 = st.form_submit_button('Submit Nama Penilai 👈')
        
        st.caption('wajib di Submit untuk memulai')
        
        # logika default nya, nanti ubah 
        if 'cari_1' not in st.session_state:
            st.session_state['cari_1'] = search_1
        
        ## ini benar
        # LOGIKA LOGIN NIK NYA
        if b1 and korek_nik == search_1:
            st.write('Nama Penilai ***' + search_1 + '*** & ' + 'NIK ***' + str(nik_eval) + '***')
            st.success('Succes login, selamat menilai!', icon="✅")
            st.caption('abaikan jika sudah login')
            
            st.session_state['cari_1'] = search_1
                
        elif b1 and korek_nik != search_1:
            st.error("⚠️ NIK tidak di sesuai, tolong masukan NIK dengan benar, ya")   
            
        else:
            st.info('NIK harus sesuai dengan penilai & harus angka, abaikan jika sudah login!')

            
            
###########################
##### FORM 2 / NAMA YANG AKAN DINILAI MOMENT  #####
############################

    with st.form('form_77'):
        st.header('2. Nama Yang Akan Dinilai')
        
        ## pilih nama yang akan dinilai
        search_2 = st.selectbox('Pilih Nama Yang Akan Dinilai',
                                list(nama_yang_dinilai(st.session_state['cari_1'])),
                                help = 'Nama Yang akan di nilai disini ya')
        
        # CTA SUBMIT NAMA 
        b2 = st.form_submit_button('Submit Nama 👈')
        
        # LOGIKA NYA 
        if b1 and b2 and korek_nik == search_1:
            st.write('Nama Yang akan di nilai **' + search_2 + '***')

        else:
            st.info('Cari nama yang akan dinilai')
            

        # SUMMARY NYA
        st.header('3. Summary')
        test_masuk = st.markdown('Penilai ***' + st.session_state['cari_1'] + '*** & ' + 'NIK ' + '***' + str(nik_eval) + '***' + ' Nama Yang akan di nilai ' +'***' + search_2 + '***.')
        st.markdown('') # < here for space 
        st.markdown('')
        st.markdown('')
        
        # COPYRIGHT 
        st.caption("<h6 style='text-align: center;'>© 2023 Copyright by Mega Perintis. All Rights Reserved.</h6>", unsafe_allow_html=True)
        
    



###########################
##### QUESTION MOMENT #####
############################



###########################
##### QUESTION TO STAFFLEVEL  #####
############################

staff_question = {'1. Menunjukkan kesadaran diri. Menanggapi dengan pemikiran yang positif saat menghadapi tantangan atau peluang baru. Berupaya mengembangkan diri dan belajar. Mudah beradaptasi dengan berbagai cara kerja.':
                  ('(1) Tidak dapat beradaptasi saat menghadapi masalah, membiarkan kesalahan atau masalah menghambat kemajuan; tidak belajar dari pengalaman dan terus menghadapi masalah yang sama.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Pulih dari kesalahan dan kemunduran; terbuka untuk saran dan kesempatan belajar.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Cepat menyesuaikan untuk menghadapi kendala dan belajar dari pengalaman; mencari peluang untuk mengumpulkan saran serta memperoleh keterampilan dan pengalaman baru.'),
                  
                  '2. Mendukung pertukaran informasi yang penting secara cepat dan terbuka antara diri sendiri dan orang lain di dalam perusahaan. Mendorong penyampaian ide dan pendapat secara terbuka. Menunjukkan keterampilan mendengar secara aktif. Meminta klarifikasi saat informasi atau pesan tidak jelas':
                  ('(1) Memberi informasi terlalu banyak atau terlalu sedikit dan kesulitan menyampaikan poin penting; melewatkan peluang untuk mendengarkan dan berbagi informasi.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Menyampaikan gagasan dengan cara yang mudah dipahami, berbagi informasi yang bermanfaat dengan orang lain; mendengarkan dengan baik untuk memahami sudut pandang orang lain.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Berkomunikasi efektif dalam lisan maupun tulisan; mendengarkan dengan saksama dan berbagi informasi dengan proaktif di seluruh bagian.'),
                  
                  '3. Bertindak selaras dengan nilai Mega Perintis untuk memperoleh kepercayaan orang lain melalui etika bisnis yang baik, ketulusan dan pelaksanaan komitmen. Menunjukkan konsistensi antara perkataan dan perbuatan':
                  ('(1) Tidak jujur; bertindak tidak sesuai dengan kebijakan atau praktik tertulis; menyalahkan orang lain atas kesalahan.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Membangun kepercayaan melalui perilaku yang jujur dan konsisten; biasanya mengikuti kebijakan dan praktik tertulis; bertanggung jawab atas kinerja dan tindakannya.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Memegang erat etika pekerjaan dan kejujuran; selalu mengikuti pedoman kebijakan dan praktik; langsung bertanggung jawab atas kinerja dan tindakannya sendiri, tidak menyalahkan orang lain.'),
                   
                   '4. Menyuarakan dan membangkitkan komitmen pada visi dan rencana tindakan yang selaras dengan tujuan perusahaan. Menanamkan optimisme dan tanggung jawab di seluruh perusahaan, membantu orang lain membayangkan kemungkinan yang dapat dicapai':
                   ('(1) Bersikap negatif atau tidak berkomitmen pada perusahaan; jarang berbagi ide dengan orang lain; sudut pandang tidak didukung dengan dasar pemikiran.',
                    '(2) Antara nilai 1 dan nilai 3.',
                    '(3) Menampilkan sikap positif yang mempengaruhi orang lain; membahas ide dan sudut pandang dan mendukung pandangan tersebut dengan dasar pemikiran yang beralasan.',
                    '(4) Antara nilai 3 dan nilai 5.',
                    '(5) Berbagi ide dan sudut pandang dengan orang lain secara terbuka; mendukung orang lain dengan percaya diri dan dasar pemikiran yang matang dan meyakinkan.'),
                   
                   '5 .Membangun hubungan dan jaringan di dalam perusahaan yang meningkatkan tingkat kerjasama, kolaborasi, dan kepercayaan di seluruh jajaran, serta dengan pelanggan dan mitra kerja, demi mewujudkan budaya yang mengutamakan perusahaan. Menangani konflik secara konstruktif dalam situasi yang sulit atau tegang.':
                   ('(1) Berhubungan baik dengan sebagian orang saja; tidak menghormati melibatkan orang lain dalam masalah yang mempengaruhi mereka; membiarkan perselisihan merusak hubungan.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Berhubungan dengan orang lain secara saling menghormati; melibatkan dan mendengar sudut pandang orang dalam masalah yang mempengaruhi mereka.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Menjalin jaringan hubungan dan selalu berinteraksi dengan orang lain secara positif dan menghormati; berfokus pada menjaga hubungan kerjasama, bahkan ketika terjadi perselisihan.'),
                    
                    '6 .Mendukung orang lain untuk memanfaatkan dan mengembangkan kemampuannya. Memberi saran dan dukungan, serta berbagi praktik terbaik. Efektif mengembangkan, mengelola, dan mempertahankan talenta penting. Mengenali dan menghargai kinerja yang baik dan membenahi masalah kinerja rendah secara konstruktif.':
                    ('(1) Memberi saran yang tidak tulus, menyinggung perasaan, atau tidak seimbang; menghindari memberi saran; jarang berbagi pengalaman dan keahliannya dengan orang lain.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Memberi saran yang jujur; mau berbagi pengalaman dan keahliannya dengan orang lain saat diminta atau saat diperlukan untuk mengatasi masalah atau persoalan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Memberi saran yang jujur, dengan cara yang menghormati dan mendukung; sering berbagi pengalaman dan keahliannya tanpa pamrih untuk membantu orang lain.'),
                    
                    '7. Memahami model bisnis Mega Perintis (industri retail), strategi dan produknya. Menyelaraskan kemampuan dengan strategi perusahaan untuk menangkap tren yang muncul, mengatasi ancaman dari pesaing, memenuhi kebutuhan pasar, memberi manfaat bagi pelanggan dan mempertahankan keunggulan kompetitif Mega Perintis.':
                    ('(1) Hanya memiliki pemahaman terbatas tentang bisnis perusahaan; tidak melihat hubungan penting antara pekerjaannya dan kerangka operasi perusahaan; menangani masalah taktis tanpa mempertimbangkan secara saksama.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Memahami aspek-aspek penting dalam bisnis; secara efektif memahami tentang arti pekerjaannya dalam kerangka operasi perusahaan dan menggunakan hal ini untuk mengarahkan pekerjaannya dengan berupaya mencapai tujuan dan strategi utama kelompok kerja.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Menunjukkan pemahaman yang kuat dan menyeluruh tentang bisnis dan strategi perusahaan; menyadari dengan jelas arti pekerjaannya dalam kerangka operasi perusahaan dan menyelaraskan kegiatannya dengan tujuan dan strategi kelompok kerja.'),
                    
                    '8. Menghasilkan dan memperjuangkan ide, pendekatan, solusi dan inisiatif yang baru dan inovatif. Mendukung lingkungan yang melakukan perbaikan berkelanjutan dan selalu mempertanyakan kondisi saat ini untuk meningkatkan manfaat bagi perusahaan dan pelanggan':
                    ('(1) Tidak secara aktif mendukung upaya perbaikan atau menyarankan perubahan; membiarkan kegagalan proses berdampak pada kinerja.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Mendukung upaya perbaikan, mengidentifikasi peluang untuk meningkatkan mutu kerja atau mengatasi kegagalan proses.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mencari peluang untuk menyempurnakan proses dan praktik yang ada; mendukung penerapan upaya ini secara tepat dan efisien.'),
                    
                    '9. Memadukan informasi dari berbagai sumber di seluruh perusahaan untuk mengevaluasi berbagai alternatif dan mengambil keputusan efektif yang mengutamakan kepentingan perusahaan dan pelanggan. Menarik kesimpulan yang tepat dan bermanfaat dari informasi kuantitatif dan kualitatif.':
                    ('(1) Mengambil keputusan yang tidak mempertimbangkan informasi penting, potensi konsekuensi, aturan atau prosedur yang ada, sehingga menghasilkan keputusan yang meleset dalam beberapa segi.',
                         '(2) Antara nilai 1 dan nilai 3',
                         '(3) Mengambil keputusan yang wajar tentang masalah dan persoalan; mengusulkan solusi yang sesuai berdasarkan informasi yang tersedia serta aturan dan prosedur yang ada.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mengambil keputusan yang baik dan cepat dengan menggunakan aturan dan prosedur yang ada untuk memperoleh solusi yang wajar dan realistis; mempertimbangkan potensi dampak dari berbagai tindakan.'),
                    
                    '10. Mengembangkan solusi yang mengutamakan pelanggan. Menyediakan pengalaman, produk dan layanan yang memenuhi atau melebihi persyaratan pelanggan (internal dan eksternal). Terus-menerus mengidentifikasi dan membuat cara baru untuk meningkatkan kepuasan dan kesetiaan pelanggan serta memastikan masalah pelanggan dapat diatasi.':
                    ('(1) Tidak memiliki pengetahuan penting tentang kebutuhan pelanggan; menyulitkan penyediaan sumber daya atau pemecahan masalah yang tepat; tidak memastikan masalah pelanggan ditindaklanjuti sampai tuntas.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Memahami kebutuhan pelanggan; menggunakan sumber daya yang tersedia untuk menyelidiki dan mengatasi masalah pelanggan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Selalu melampaui pengharapan pelanggan; berusaha mengumpulkan dan memahami saran pelanggan untuk mengidentifikasi kebutuhan mereka dengan tepat.'),
                    
                    '11. Memfokuskan, menyelaraskan dan mengoptimalkan penggunaan sumber daya untuk mencapai tujuan. Menunjukkan prioritas, mengelola kinerja, menuntut tanggung jawab diri sendiri dan orang lain dalam menyelesaikan pekerjaan dan menyingkirkan rintangan secara efektif dan efisien demi meraih sukses.':
                   ('(1) Kesulitan memahami atau menangani prioritas; kurang mengerti rintangan yang sebenarnya dapat dicegah; perhatian mudah teralih atau mengabaikan tugas setengah jalan.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Mampu membereskan pekerjaan; rajin bekerja, bertindak untuk merampungkan pekerjaan dan penugasan sesuai pengharapan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Selalu berfokus pada prioritas terpenting, bahkan saat waktu terbatas dan terkendala sumber daya; terus berupaya dan dapat diandalkan untuk merampungkan tugas melebihi pengharapan.'),
                    
                    '12. Mengelola perubahan agar perusahaan mencapai sukses. Bekerja secara produktif saat menghadapi ketidakjelasan atau ketidakpastian. Membantu orang lain menyambut perubahan secara positif.':
                    ('(1) Hampir tidak melakukan apa-apa untuk mengikuti perubahan ekspektasi kerja dan kriteria kesuksesan; selalu menolak atau menghindari perubahan; melewatkan peluang atau menolak cara kerja baru.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Mengelola sesuai dengan pengharapan kinerja dan kriteria sukses yang disampaikan; bersikap terbuka terhadap perubahan; beradaptasi dengan cara kerja baru, meski mungkin tidak termasuk yang pertama mengikutinya.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Sering bertanya proaktif untuk mengetahui perubahan pengharapan kinerja dan kriteria sukses; keluar dari zona kenyamanan untuk menyambut perubahan; cepat beradaptasi dengan cara kerja baru.'),       
                 }





###########################
##### QUESTION TO SECTION / OFFICER LEVEL  #####
############################

staff_section_dan_officer = {'1. Menunjukkan kesadaran diri. Menanggapi dengan pemikiran yang positif saat menghadapi tantangan atau peluang baru. Berupaya mengembangkan diri dan belajar. Mudah beradaptasi dengan berbagai cara kerja.':
                  ('(1) Tidak beradaptasi dengan perubahan situasi dan membiarkan hambatan mencegah kemajuan; menghindari saran dan lebih suka menjaga keterampilan yang sudah dimiliki.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Menyesuaikan sebagaimana diperlukan untuk meraih kemajuan meskipun ada hambatan, kesulitan dan kesalahan; menerima saran dan terbuka terhadap kesempatan untuk belajar dan memperluas sudut pandang.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Cepat beradaptasi dengan perubahan situasi; menunjukkan tingkat ketahanan tinggi dalam menghadapi kendala; meminta dan menerapkan saran, mengidentifikasi kesempatan belajar untuk memperoleh keterampilan baru.'),
                  
                  '2. Mendukung pertukaran informasi yang penting secara cepat dan terbuka antara diri sendiri dan orang lain di dalam perusahaan. Mendorong penyampaian ide dan pendapat secara terbuka. Menunjukkan keterampilan mendengar secara aktif. Meminta klarifikasi saat informasi atau pesan tidak jelas':
                  ('(1) Memberi informasi kurang atau terlalu banyak dalam laporan dan dokumentasi; kesulitan mengungkapkan pendapat dalam percakapan; tidak mendengarkan dengan baik.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Berkomunikasi secara efektif dengan orang lain, berbagi informasi secara jelas dan ringkas; menghasilkan laporan dan dokumentasi yang jelas; berkomunikasi dan mendengarkan dengan baik.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Berbagi informasi secara jelas dan profesional; memberi tingkat perincian yang tepat dalam laporan dan dokumentasi; menggunakan keterampilan mendengar secara aktif agar orang lain merasa didengar dan dipahami.'),
                  
                  '3. Bertindak selaras dengan nilai Mega Perintis untuk memperoleh kepercayaan orang lain melalui etika bisnis yang baik, ketulusan dan pelaksanaan komitmen. Menunjukkan konsistensi antara perkataan dan perbuatan':
                  ('(1) Menunjukkan ketidakjujuran tentang masalah; bertindak tidak sesuai dengan kebijakan atau praktik tertulis; cepat menyalahkan orang lain atas kesalahan..',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Membangun kepercayaan dan kredibilitas melalui perilaku yang jujur dan konsisten; mengikuti kebijakan dan praktik tertulis; bertanggung jawab atas kinerja dan tindakannya.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Teladan etika pekerjaan dan kejujuran; selalu mengikuti pedoman kebijakan dan praktik; berfokus pada masalah, bukan menyalahkan orang lain.'),
                   
                   '4. Menyuarakan dan membangkitkan komitmen pada visi dan rencana tindakan yang selaras dengan tujuan perusahaan. Menanamkan optimisme dan tanggung jawab di seluruh perusahaan, membantu orang lain membayangkan kemungkinan yang dapat dicapai':
                   ('(1) Bersikap negatif pada perusahaan; tidak memberi dasar pemikiran atau informasi yang memadai untuk mendukung saran-sarannya; serta kesulitan memperoleh dukungan.',
                    '(2) Antara nilai 1 dan nilai 3.',
                    '(3) Menampakkan citra positif yang mempengaruhi orang lain; menyampaikan dasar pemikiran yang relevan sehingga memperoleh dukungan orang lain.',
                    '(4) Antara nilai 3 dan nilai 5.',
                    '(5) Antusias menggalang orang lain untuk mendukung tujuan bersama; memberi dasar pemikiran untuk ide-idenya secara bersemangat dan percaya diri ke orang lain, sehingga memperoleh komitmen mereka.'),
                   
                   '5. Membangun hubungan dan jaringan di dalam perusahaan yang meningkatkan tingkat kerjasama, kolaborasi, dan kepercayaan di seluruh jajaran, serta dengan pelanggan dan mitra kerja, demi mewujudkan budaya yang mengutamakan perusahaan. Menangani konflik secara konstruktif dalam situasi yang sulit atau tegang.':
                   ('(1) Berhubungan baik dengan sebagian orang saja; tidak menghormati atau memperhatikan sudut pandang orang lain; membiarkan situasi sulit merusak hubungan.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Berhubungan dengan orang lain secara profesional dan menghormati; mendengar sudut pandang mereka bahkan dalam situasi sulit; menjaga hubungan di seluruh perusahaan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Selalu berinteraksi dengan orang lain secara profesional dan menghormati; fokus pada kepentingan bersama dan menjaga hubungan positif, bahkan dalam situasi sulit atau tegang.'),
                    
                    '6. Mendukung orang lain untuk memanfaatkan dan mengembangkan kemampuannya. Memberi saran dan dukungan, serta berbagi praktik terbaik. Efektif mengembangkan, mengelola, dan mempertahankan talenta penting. Mengenali dan menghargai kinerja yang baik dan membenahi masalah kinerja rendah secara konstruktif.':
                    ('(1) Memberi saran yang tidak tulus, menyinggung perasaan; menghindari memberi saran sama sekali atau melakukannya sesekali saja; jarang berbagi pengalaman dan keahliannya dengan orang lain.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Memberi saran yang jujur dan bermanfaat kepada orang lain; mau berbagi pengalaman dan keahliannya saat diminta atau saat diperlukan untuk mengatasi masalah atau persoalan..',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Secara proaktif memberi saran yang membangun, bermanfaat; sering berbagi pengalaman dan keahliannya tanpa pamrih untuk membantu orang lain.'),
                    
                    '7. Memahami model bisnis Mega Perintis (industri retail), strategi dan produknya. Menyelaraskan kemampuan dengan strategi perusahaan untuk menangkap tren yang muncul, mengatasi ancaman dari pesaing, memenuhi kebutuhan pasar, memberi manfaat bagi pelanggan dan mempertahankan keunggulan kompetitif Mega Perintis.':
                    ('(1) Menunjukkan pemahaman yang terbatas tentang kebutuhan pelanggan; gagal memaksimalkan potensi keuntungan dan meminimalkan tindakan yang berisiko.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Menerapkan pemahaman tentang kebutuhan pelanggan untuk memberi saran tentang berbagai peluang yang sesuai dengan prioritas organisasi; memaksimalkan potensi keuntungan dan meminimalkan risiko.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mengidentifikasi dan mengejar masalah yang terkait dengan pelanggan; mendukung strategi dan prioritas perusahaan sementara mengajukan saran yang meningkatkan potensi keuntungan dan meminimalkan risiko.'),
                    
                    '8. Menghasilkan dan memperjuangkan ide, pendekatan, solusi dan inisiatif yang baru dan inovatif. Mendukung lingkungan yang melakukan perbaikan berkelanjutan dan selalu mempertanyakan kondisi saat ini untuk meningkatkan manfaat bagi perusahaan dan pelanggan':
                    ('(1) Tidak secara aktif mendukung upaya perbaikan; membiarkan kegagalan proses atau masalah lain berdampak negatif pada kinerja.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Mendukung upaya perbaikan, mengidentifikasi peluang untuk meningkatkan kerja atau mengatasi kegagalan proses; mengajukan ide dan solusi untuk meningkatkan fungsi yang ada; mendukung orang lain dalam mempertimbangkan cara baru..',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mengambil tindakan ketika dihadapkan dengan kesempatan untuk memperbaiki proses dan praktik yang ada; menghasilkan dan mendukung penerapan ide dan solusi; secara aktif mendorong orang lain untuk mencari potensi perbaikan.'),
                    
                    '9. Memadukan informasi dari berbagai sumber di seluruh perusahaan untuk mengevaluasi berbagai alternatif dan mengambil keputusan efektif yang mengutamakan kepentingan perusahaan dan pelanggan. Menarik kesimpulan yang tepat dan bermanfaat dari informasi kuantitatif dan kualitatif.':
                    ('(1) Mengambil keputusan tidak mempertimbangkan informasi penting, kemungkinan konsekuensi, peraturan atau prosedur yang ada; kesulitan menarik kesimpulan dari informasi yang rumit atau ambigu..',
                         '(2) Antara nilai 1 dan nilai 3',
                         '(3) Secara tepat menganalisis informasi yang tersedia dan kemungkinan penyebabnya; mengambil keputusan yang wajar berdasarkan informasi yang tersedia serta kebijakan, prosedur dan nilai perusahaan yang relevan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Secara efektif memadukan beragam informasi dari berbagai sumber dan sudut pandang; selalu mengambil keputusan yang baik dan efektif yang menggunakan kebijakan, prosedur dan nilai perusahaan untuk mencapai solusi yang berdampak positif.'),
                    
                    '10. Mengembangkan solusi yang mengutamakan pelanggan. Menyediakan pengalaman, produk dan layanan yang memenuhi atau melebihi persyaratan pelanggan (internal dan eksternal). Terus-menerus mengidentifikasi dan membuat cara baru untuk meningkatkan kepuasan dan kesetiaan pelanggan serta memastikan masalah pelanggan dapat diatasi.':
                    ('(1) Tidak berusaha mengidentifikasi dan memenuhi persyaratan, harapan atau kebutuhan pelanggan terlebih dulu; melewatkan peluang untuk meminta saran atau mengatasi masalah dengan cepat.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Memberi layanan pelanggan secara memuaskan dan berkualitas; menggunakan sumber daya yang tersedia untuk mengetahui dan memenuhi persyaratan, harapan dan kebutuhan pelanggan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Melakukan dialog proaktif untuk mengidentifikasi kebutuhan pelanggan; meminta saran pelanggan dan mencoba peluang untuk menaikkan tingkat layanan.'),
                    
                    '11. Memfokuskan, menyelaraskan dan mengoptimalkan penggunaan sumber daya untuk mencapai tujuan. Menunjukkan prioritas, mengelola kinerja, menuntut tanggung jawab diri sendiri dan orang lain dalam menyelesaikan pekerjaan dan menyingkirkan rintangan secara efektif dan efisien demi meraih sukses.':
                   ('(1) Menunjukkan rasa tidak berkomitmen pada tujuan yang diprioritaskan atau terkadang tidak melibatkan diri; kesulitan menjaga fokus dan energi ketika menyelesaikan pekerjaan dengan cepat.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Mencurahkan waktu dan tenaga untuk mengejar tujuan yang diprioritaskan, menunjukkan komitmen untuk mencapai hasil yang bermakna; menunjukkan kemampuan multitasking dan menyelesaikan pekerjaan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Menunjukkan rasa bersemangat dan bertanggung jawab; berusaha keras dan bertindak cepat untuk mendorong penyelesaian tugas yang baik; berfokus pada prioritas terpenting.'),
                    
                    '12. Mengelola perubahan agar perusahaan mencapai sukses. Bekerja secara produktif saat menghadapi ketidakjelasan atau ketidakpastian. Membantu orang lain menyambut perubahan secara positif.':
                    ('(1) Hampir tidak mengikuti perubahan ekspektasi dan kriteria kesuksesan; selalu menolak atau menghindari perubahan dan melewatkan peluang untuk membantu orang lain mempersiapkan diri menghadapi dampak perubahan.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Mengelola sesuai dengan ekspektasi kinerja dan kriteria kesuksesan yang disampaikan; menunjukkan sikap terbuka terhadap perubahan; membantu orang lain mempersiapkan diri dan mengelola dampak perubahan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Sering bertanya proaktif untuk mengetahui perubahan ekspektasi kinerja dan kriteria kesuksesan; keluar dari zona nyaman untuk menerima perubahan; mendukung orang lain mempersiapkan diri untuk perubahan yang akan terjadi.'),
                   
                     }



###########################
##### QUESTION TO DIVISION HEAD LEVEL  #####
############################

division_head = {'1. Menunjukkan kesadaran diri. Menanggapi dengan pemikiran yang positif saat menghadapi tantangan atau peluang baru. Berupaya mengembangkan diri dan belajar. Mudah beradaptasi dengan berbagai cara kerja.':
                  ('(1) Kurang menyesuaikan pendekatan sebagaimana diperlukan untuk beradaptasi dengan situasi yang berubah, tergelincir oleh situasi penuh tekanan; menghindari saran dan tidak tertarik belajar dari orang lain..',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Menyesuaikan pendekatan sebagaimana diperlukan untuk mencapai kemajuan meskipun prioritas berubah atau situasi penuh tekanan; menerima saran saat diberikan; tertarik belajar hal-hal baru..',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Bertindak efektif bahkan dalam situasi bertekanan tinggi; fleksibel dan memiliki pemikiran yang panjang saat menghadapi perubahan prioritas; mencari saran dan kesempatan untuk belajar dari orang lain.'),
                  
                  '2. Mendukung pertukaran informasi yang penting secara cepat dan terbuka antara diri sendiri dan orang lain di dalam perusahaan. Mendorong penyampaian ide dan pendapat secara terbuka. Menunjukkan keterampilan mendengar secara aktif. Meminta klarifikasi saat informasi atau pesan tidak jelas':
                  ('(1) Memberi perincian terlalu sedikit atau informasi terlalu banyak; berkomunikasi hanya dengan tingkat jabatan tertentu; kurang berbagi informasi penting dengan pihak yang memerlukannya; kurang mendengarkan sudut pandang orang lain dengan saksama.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Berkomunikasi efektif dengan orang lain dari berbagai tingkat jabatan; berbagi informasi yang jelas dan ringkas bagi orang yang memerlukannya; mendengarkan orang lain.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Berbagi informasi yang jelas dan tepat waktu secara menarik; secara proaktif berbagi kabar terbaru dan informasi ke seluruh organisasi; dengan terampil menyesuaikan pendekatan komunikasi.'),
                  
                  '3. Bertindak selaras dengan nilai Mega Perintis untuk memperoleh kepercayaan orang lain melalui etika bisnis yang baik, ketulusan dan pelaksanaan komitmen. Menunjukkan konsistensi antara perkataan dan perbuatan':
                  ('(1) Kurang bertindak sesuai dengan visi, nilai dan tujuan perusahaan; memperlakukan orang secara tidak adil; menghindari pembahasan tentang pertimbangan etika suatu masalah; menutupi kesalahan atau menyalahkan orang lain.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Membangun kepercayaan melalui perilaku yang adil, beretika dan konsisten; secara jujur mengakui kesalahannya; memastikan bahwa praktik terbaik dan pelajaran penting disebarluaskan ke seluruh perusahaan.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Maju untuk menghadapi masalah dan persoalan sulit secara proaktif; memastikan praktik terbaik diterapkan sepenuhnya di seluruh perusahaan dan tertanam dalam cara berbisnis.'),
                   
                   '4. Menyuarakan dan membangkitkan komitmen pada visi dan rencana tindakan yang selaras dengan tujuan perusahaan. Menanamkan optimisme dan tanggung jawab di seluruh perusahaan, membantu orang lain membayangkan kemungkinan yang dapat dicapai':
                   ('(1) Kurang berupaya mendorong komitmen atau menginspirasi orang lain untuk melampaui tujuan; kurang memiliki dasar pemikiran yang jelas, kesulitan dalam mengajukan ide.',
                    '(2) Antara nilai 1 dan nilai 3.',
                    '(3) Membangkitkan tanggung jawab dan mendorong orang lain bekerja sebaik-baiknya; memiliki logika dan dasar pemikiran yang cukup saat menyajikan ide dan menanggapi reaksi orang lain.',
                    '(4) Antara nilai 3 dan nilai 5.',
                    '(5) Membuat lingkungan kerja berenergi, penuh kegairahan dan menginspirasi orang untuk menjadi lebih unggul; menawarkan solusi yang menguntungkan semua pihak.'),
                   
                   '5. Membangun hubungan dan jaringan di dalam perusahaan yang meningkatkan tingkat kerjasama, kolaborasi, dan kepercayaan di seluruh jajaran, serta dengan pelanggan dan mitra kerja, demi mewujudkan budaya yang mengutamakan perusahaan. Menangani konflik secara konstruktif dalam situasi yang sulit atau tegang.':
                   ('(1) Kurang melibatkan pihak lain dalam rencana ataupun berupaya memahami pandangan mereka; kurang memiliki empati atau keterbukaan bagi orang lain sehingga membatasi kualitas hubungan; berhubungan baik dengan sebagian orang atau tingkat saja.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Melibatkan pihak lain sebagaimana diperlukan; menyelesaikan pandangan yang bertentangan; menjalin hubungan baik —apapun jabatan, kepribadian atau latar belakangnya— dengan bersikap hormat dan terbuka.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mendorong kolaborasi dengan melibatkan pihak lain dalam keputusan dan rencana; secara terampil melakukan penyelarasan dan diskusi yang konstruktif dan langsung; menjaga hubungan yang positif dengan banyak orang di seluruh perusahaan.'),
                    
                    '6. Mendukung orang lain untuk memanfaatkan dan mengembangkan kemampuannya. Memberi saran dan dukungan, serta berbagi praktik terbaik. Efektif mengembangkan, mengelola, dan mempertahankan talenta penting. Mengenali dan menghargai kinerja yang baik dan membenahi masalah kinerja rendah secara konstruktif.':
                    ('(1) Kurang memberikan dukungan untuk membantu orang lain; enggan berbagi pengalamannya dengan orang lain; memberi saran yang tidak tepat atau tidak peka, atau menghindari memberi saran..',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Memberi saran jujur dan bermanfaat tentang kinerja serta berbagi pengalamannya dengan orang lain; menuntut diri dan orang lain bertanggung jawab atas mengembangkan bawahan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Secara proaktif membantu orang lain untuk mengidentifikasi dan memprioritaskan tujuan pengembangan diri mereka; memberi saran yang jelas dan terarah untuk meningkatkan kinerja orang lain; mendorong orang lain berbagi keahlian di seluruh perusahaan.'),
                    
                    '7. Memahami model bisnis Mega Perintis (industri retail), strategi dan produknya. Menyelaraskan kemampuan dengan strategi perusahaan untuk menangkap tren yang muncul, mengatasi ancaman dari pesaing, memenuhi kebutuhan pasar, memberi manfaat bagi pelanggan dan mempertahankan keunggulan kompetitif Mega Perintis.':
                    ('(1) Memprioritaskan bidangnya tapi kurang selaras dengan strategi perusahaan yang lebih luas; kurang menyeimbangkan persyaratan jangka pendek dengan rencana jangka panjang; terlalu berfokus pada perincian dan masalah taktis jangka pendek.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Menyelaraskan pekerjaan divisinya dengan tujuan perusahaan; memiliki pemahaman baik tentang aspek-aspek kekuatan, kelemahan, peluang dan ancaman di bidangnya; mencapai keseimbangan antara kegiatan jangka panjang dan sehari-hari.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Menerapkan wawasan mendalam tentang pasar dan industri saat membuat strategi; memilih prioritas yang paling bermanfaat agar selaras dengan kebutuhan perusahaan; menyeimbangkan sepenuhnya masalah skala perusahaan dan kegiatan sehari-hari.'),
                    
                    '8. Menghasilkan dan memperjuangkan ide, pendekatan, solusi dan inisiatif yang baru dan inovatif. Mendukung lingkungan yang melakukan perbaikan berkelanjutan dan selalu mempertanyakan kondisi saat ini untuk meningkatkan manfaat bagi perusahaan dan pelanggan':
                    ('(1) Kurang terlalu ingin tahu atau berpikiran terbuka saat menghadapi masalah; menolak upaya orang lain untuk mempertanyakan proses yang ada; meremehkan upaya orang lain yang berusaha memandang masalah dalam cara baru dan berbeda.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Tampak tertarik dan terbuka saat mendekati masalah; menghasilkan ide inovatif untuk meningkatkan hasil dan efisiensi; mendukung orang lain untuk mempertimbangkan cara baru dalam memandang masalah.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Sangat ingin tahu dan berpikiran terbuka saat mendekati masalah dan proses; menghasilkan ide inovatif yang mempertanyakan pemikiran kondisi saat ini dan menciptakan lingkungan yang mendorong orang lain melakukan hal yang sama.'),
                    
                    '9. Memadukan informasi dari berbagai sumber di seluruh perusahaan untuk mengevaluasi berbagai alternatif dan mengambil keputusan efektif yang mengutamakan kepentingan perusahaan dan pelanggan. Menarik kesimpulan yang tepat dan bermanfaat dari informasi kuantitatif dan kualitatif.':
                    ('(1) Berfokus hanya pada beberapa jenis informasi kuantitatif; hanya mengidentifikasi tema parsial dan tidak mengetahui akar penyebab masalah; kurang mempertimbangkan faktor-faktor penting yang terkait dengan suatu alternatif.',
                         '(2) Antara nilai 1 dan nilai 3',
                         '(3) Mengevaluasi persoalan dengan memadukan informasi dengan cara menyoroti masalah penting dan akar penyebabnya; mempertimbangkan masalah penting, biaya dan manfaat yang terkait dengan berbagai alternatif.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Melakukan analisis data dari berbagai sumber; mencapai solusi yang jelas dan logis; menerapkan logika dan dasar pemikiran yang kuat untuk mengambil keputusan matang yang benar-benar mempertimbangkan biaya dan manfaat terkait.'),
                    
                    '10. Mengembangkan solusi yang mengutamakan pelanggan. Menyediakan pengalaman, produk dan layanan yang memenuhi atau melebihi persyaratan pelanggan (internal dan eksternal). Terus-menerus mengidentifikasi dan membuat cara baru untuk meningkatkan kepuasan dan kesetiaan pelanggan serta memastikan masalah pelanggan dapat diatasi.':
                    ('(1) Kurang meminta saran atau menangani kebutuhan pelanggan secara proaktif; kurang efektif melacak kinerja atau berusaha menyempurnakan sistem atau proses yang dapat memudahkan pelanggan.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Secara umum menunaikan komitmen pada pelanggan, menggunakan alat bantu yang ada untuk melacak kemajuan; mencari peluang untuk mengantisipasi kebutuhan pelanggan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Memberi layanan di atas harapan; secara aktif meminta saran dan memantau kinerja untuk memastikan masalah diselesaikan tuntas; memahami kebutuhan pelanggan dan secara proaktif mencoba berbagai cara untuk menerapkan sistem dan proses yang memudahkan pelanggan.'),
                    
                    '11. Memfokuskan, menyelaraskan dan mengoptimalkan penggunaan sumber daya untuk mencapai tujuan. Menunjukkan prioritas, mengelola kinerja, menuntut tanggung jawab diri sendiri dan orang lain dalam menyelesaikan pekerjaan dan menyingkirkan rintangan secara efektif dan efisien demi meraih sukses.':
                   ('(1) Membiarkan orang lain kebingungan tentang apa yang diharapkan dari mereka; melewatkan kesempatan untuk mendelegasikan tugas; menetapkan tujuan yang mudah dicapai bagi diri sendiri dan orang lain; melewatkan peluang untuk menaikkan standar kinerja.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Menyampaikan harapan untuk penugasan; secara umum menuntut orang lain bertanggung jawab dalam memenuhinya; menetapkan tujuan menantang untuk diri sendiri dan orang lain.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Menetapkan harapan jelas untuk penugasan dan mendelegasikan tugas kepada orang yang tepat; selalu menetapkan tujuan yang menantang bagi diri sendiri dan orang lain; mendorong semua orang memenuhi pengharapan.'),
                    
                    '12. Mengelola perubahan agar perusahaan mencapai sukses. Bekerja secara produktif saat menghadapi ketidakjelasan atau ketidakpastian. Membantu orang lain menyambut perubahan secara positif.':
                    ('(1) Kurang tertarik meminta atau menerapkan saran dari para pemangku kepentingan, sehingga kesulitan memperoleh penerimaan terhadap perubahan; kurang mengantisipasi penolakan terhadap perubahan.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Menerapkan inisiatif perubahan dan berupaya merangsang diskusi tentang perubahan; mengidentifikasi dan mendukung perubahan bermanfaat dalam perusahaan; secara efektif menangani kekhawatiran atau penolakan dari orang lain.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Menerapkan perubahan secara sukses di seluruh perusahaan; secara proaktif melibatkan para pemangku kepentingan yang terpengaruh; cepat mengidentifikasi perubahan yang berdampak besar dan secara antusias maju untuk mendukungnya agar diterima semua pihak.'),
                   
                     }




###########################
##### QUESTION TO DEPT HEAD LEVEL  #####
############################

department_head = {'1. Menunjukkan kesadaran diri. Menanggapi dengan pemikiran yang positif saat menghadapi tantangan atau peluang baru. Berupaya mengembangkan diri dan belajar. Mudah beradaptasi dengan berbagai cara kerja.':
                  ('(1) Ragu saat membahas pengembangan diri; membiarkan kesalahan mencegah kemajuan; menghindari saran dan tidak mengembangkan pengetahuan atau keterampilan baru.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Menyadari kemampuannya, tetapi tidak terlalu menyadari kesempatan pengembangan diri; secara efektif menangani situasi sulit; menerima saran dan terbuka terhadap kesempatan untuk mempelajari pengetahuan dan keterampilan baru.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Sangat menyadari kemampuan dan kebutuhan pengembangan dirinya; secara aktif mencari pembelajaran pribadi dengan memperbarui pengetahuan dan keterampilan; mencari saran dan dengan mudah menerapkannya.'),
                  
                  '2. Mendukung pertukaran informasi yang penting secara cepat dan terbuka antara diri sendiri dan orang lain di dalam perusahaan. Mendorong penyampaian ide dan pendapat secara terbuka. Menunjukkan keterampilan mendengar secara aktif. Meminta klarifikasi saat informasi atau pesan tidak jelas':
                  ('(1) Tidak memberi perincian yang memadai; sulit menyampaikan ide dan tidak mampu menarik perhatian orang lain; tidak terlalu berusaha menyesuaikan gaya atau isi komunikasi.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Berkomunikasi secara efektif dengan orang lain; berbagi informasi dan sudut pandang yang jelas dan terperinci dengan orang yang memerlukannya; memilih pendekatan yang sesuai dengan orang yang dituju.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Selalu memilih gaya dan isi komunikasi yang paling sesuai untuk orang yang dituju; secara seksama mendengarkan dan secara aktif mendorong orang lain untuk memberikan pendapat langsung.'),
                  
                  '3. Bertindak selaras dengan nilai Mega Perintis untuk memperoleh kepercayaan orang lain melalui etika bisnis yang baik, ketulusan dan pelaksanaan komitmen. Menunjukkan konsistensi antara perkataan dan perbuatan':
                  ('(1) Tidak beretika dan tidak bertindak sesuai dengan kebijakan atau praktik tertulis; memperlakukan orang secara tidak adil; cepat menyalahkan orang lain atas kesalahan, bukan berfokus pada masalah dan solusi.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Membangun kepercayaan melalui perilaku yang beretika dan konsisten; mengikuti kebijakan dan praktik tertulis; bertanggung jawab atas kinerja dan tindakannya; mengingatkan jika ada kemungkinan perilaku yang tidak etis..',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Meneladankan perilaku yang menunjukkan etika terbaik; secara proaktif bertanggung jawab atas kinerja dan tindakannya; berfokus pada masalah dan solusi saat terjadi kesalahan, bukan menyalahkan orang lain.'),
                   
                   '4. Menyuarakan dan membangkitkan komitmen pada visi dan rencana tindakan yang selaras dengan tujuan perusahaan. Menanamkan optimisme dan tanggung jawab di seluruh perusahaan, membantu orang lain membayangkan kemungkinan yang dapat dicapai':
                   ('(1) Kesulitan mengaitkan dasar pemikiran dengan kebutuhan dan prioritas orang lain; tidak berusaha menumbuhkan komitmen dalam diri orang lain atau memuji upaya mereka; menciptakan situasi menang-kalah.',
                    '(2) Antara nilai 1 dan nilai 3.',
                    '(3) Memberi dasar pikiran yang relevan untuk idenya; menjelaskan potensi keuntungan dan kaitannya dengan kebutuhan orang lain sehingga memperoleh dukungan mereka; memuji bantuan orang lain.',
                    '(4) Antara nilai 3 dan nilai 5.',
                    '(5) Menunjukkan citra positif dan menjadi teladan; menyampaikan dasar pemikiran yang matang dan meyakinkan; menunjukkan keyakinan pada kemampuan orang lain untuk mencapai tujuan yang menantang.'),
                   
                   '5. Membangun hubungan dan jaringan di dalam perusahaan yang meningkatkan tingkat kerjasama, kolaborasi, dan kepercayaan di seluruh jajaran, serta dengan pelanggan dan mitra kerja, demi mewujudkan budaya yang mengutamakan perusahaan. Menangani konflik secara konstruktif dalam situasi yang sulit atau tegang.':
                   ('(1) Tidak melibatkan pihak lain dalam rencana atau tindakan; membiarkan pandangan yang bertentangan menghambat kolaborasi; berhubungan baik dengan sebagian orang saja dan tidak menghormati sudut pandang yang berbeda.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Melibatkan dan berupaya memahami sudut pandang dari bagian lain; mendukung kerjasama; berkomunikasi secara bijak dan memperlakukan orang secara profesional dan penuh hormat.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Melibatkan pihak lain secara proaktif dalam rencana dan keputusan; menerapkan sudut pandang lintas-fungsi secara efektif; cepat menyelesaikan konflik; serta mendorong kerjasama di antara berbagai bagian perusahaan.'),
                    
                    '6. Mendukung orang lain untuk memanfaatkan dan mengembangkan kemampuannya. Memberi saran dan dukungan, serta berbagi praktik terbaik. Efektif mengembangkan, mengelola, dan mempertahankan talenta penting. Mengenali dan menghargai kinerja yang baik dan membenahi masalah kinerja rendah secara konstruktif.':
                    ('(1) Tidak memberi saran kepada orang lain; melewatkan peluang untuk memberi dukungan pengembangan atau penghargaan yang diperlukan; lalai dalam menangani masalah kinerja, menganggap ringan atau menundanya.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Mendukung perencanaan dan pelaksanaan kegiatan pengembangan diri orang lain; menghargai kontribusi dan pencapaian tim; secara umum menangani masalah kinerja.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Secara proaktif melakukan perencanaan dan pelaksanaan kegiatan pengembangan diri; selalu menghargai upaya dan pencapaian positif tim; dengan cepat menangani masalah kinerja, dengan menerapkan pembimbingan secara efektif untuk meningkatkan kinerja.'),
                    
                    '7. Memahami model bisnis Mega Perintis (industri retail), strategi dan produknya. Menyelaraskan kemampuan dengan strategi perusahaan untuk menangkap tren yang muncul, mengatasi ancaman dari pesaing, memenuhi kebutuhan pasar, memberi manfaat bagi pelanggan dan mempertahankan keunggulan kompetitif Mega Perintis.':
                    ('(1) Tidak terlalu memahami gambaran utuh perusahaan; tidak menyeimbangkan masalah jangka pendek dan panjang; menangani masalah taktis tanpa benar-benar mempertimbangkan gambaran utuh.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Memahami aspek-aspek penting gambaran utuh perusahaan dan meraih keseimbangan efektif antara masalah jangka pendek dan kegiatan sehari-hari sambil berupaya mencapai tujuan penting unit kerja atau perorangan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Memiliki pemahaman yang kuat dan menyeluruh tentang gambaran utuh perusahaan; memadukan dan menyeimbangkan tema-tema luas, tren dan tujuan dengan kegiatan sehari-hari; memprioritaskan tujuan bagi unitnya.'),
                    
                    '8. Menghasilkan dan memperjuangkan ide, pendekatan, solusi dan inisiatif yang baru dan inovatif. Mendukung lingkungan yang melakukan perbaikan berkelanjutan dan selalu mempertanyakan kondisi saat ini untuk meningkatkan manfaat bagi perusahaan dan pelanggan':
                    ('(1) Melewatkan peluang bekerjasama dengan orang lain untuk menyempurnakan struktur atau proses kerja; menolak upaya orang lain untuk mempertanyakan pendekatan yang ada; meremehkan upaya orang lain yang memandang masalah dan proses dengan cara baru.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Bekerjasama atau mengumpulkan saran orang lain untuk menyempurnakan struktur atau proses kerja; mengajukan beragam ide dan solusi untuk meningkatkan fungsi yang ada; mendukung orang lain dalam mempertimbangkan cara baru memandang masalah dan proses.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Selalu bekerjasama dengan orang lain secara proaktif untuk menyempurnakan struktur atau proses kerja; menghasilkan dan mendukung penerapan ide dan solusi; secara aktif mendorong orang lain mencari perbaikan yang potensial.'),
                    
                    '9. Memadukan informasi dari berbagai sumber di seluruh perusahaan untuk mengevaluasi berbagai alternatif dan mengambil keputusan efektif yang mengutamakan kepentingan perusahaan dan pelanggan. Menarik kesimpulan yang tepat dan bermanfaat dari informasi kuantitatif dan kualitatif.':
                    ('(1) Menghasilkan analisis yang parsial atau tidak tepat; tidak mengevaluasi informasi yang tersedia secara lengkap; menunda terlalu lama atau bergerak terlalu cepat pada masalah atau peluang sehari-hari; mengambil keputusan yang meleset.',
                         '(2) Antara nilai 1 dan nilai 3',
                         '(3) Menganalisis informasi yang tersedia secara logis dan tertata; menggunakan informasi kuantitatif untuk memandu keputusan dan tindakan; mengambil keputusan yang wajar dan cepat tentang masalah dan peluang sehari-hari.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mencari informasi secara efektif sehingga dapat mengevaluasi situasi lebih baik; selalu mengambil keputusan yang baik dan cepat tentang setiap masalah dan peluang; menyeimbangkan analisis dan pengambilan keputusan yang baik.'),
                    
                    '10. Mengembangkan solusi yang mengutamakan pelanggan. Menyediakan pengalaman, produk dan layanan yang memenuhi atau melebihi persyaratan pelanggan (internal dan eksternal). Terus-menerus mengidentifikasi dan membuat cara baru untuk meningkatkan kepuasan dan kesetiaan pelanggan serta memastikan masalah pelanggan dapat diatasi.':
                    ('(1) Bereaksi terhadap permintaan atau keluhan pelanggan, tetapi tidak berusaha secara proaktif mengidentifikasi peluang perbaikan; melewatkan peluang meminta saran atau menangani masalah dengan cepat.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Memberi layanan pelanggan berkualitas menggunakan orang dan sumber daya yang tersedia; menyelidiki kebutuhan pelanggan dan berupaya mengidentifikasi peluang perbaikan; melacak kinerja terhadap persyaratan pelanggan menggunakan alat bantu yang ada.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Selalu memberi layanan terbaik bagi pelanggan; meminta saran pelanggan tentang peluang perbaikan; memastikan layanan yang di atas harapan; secara proaktif melibatkan orang dan sumber daya yang tepat pada waktu yang tepat.'),
                    
                    '11. Memfokuskan, menyelaraskan dan mengoptimalkan penggunaan sumber daya untuk mencapai tujuan. Menunjukkan prioritas, mengelola kinerja, menuntut tanggung jawab diri sendiri dan orang lain dalam menyelesaikan pekerjaan dan menyingkirkan rintangan secara efektif dan efisien demi meraih sukses.':
                   ('(1) Tidak menyampaikan langkah tindakan yang jelas; terlalu lama menyesuaikan rencana saat menghadapi rintangan; menghindari masalah sulit yang menghambat produktivitas; membiarkan kinerja buruk tidak dibenahi.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Secara umum menyampaikan pengharapan dalam penugasan dan membuat rencana bagus yang menjabarkan langkah tindakan yang diperlukan untuk mencapai tujuan; secara umum menetapkan standar kinerja tinggi bagi diri sendiri dan orang lain.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Selalu menetapkan pengharapan yang jelas dalam penugasan dan standar kinerja tinggi bagi diri sendiri dan orang lain; menjaga tingkat produktivitas yang sangat tinggi, bahkan saat menghadapi tantangan besar.'),
                    
                    '12. Mengelola perubahan agar perusahaan mencapai sukses. Bekerja secara produktif saat menghadapi ketidakjelasan atau ketidakpastian. Membantu orang lain menyambut perubahan secara positif.':
                    ('(1) Tidak secara konsisten dan jelas menyampaikan tujuan, strategi dan status perubahan; membuat rencana perubahan yang terlalu luas; tidak menuntut pertanggungjawaban orang lain atau membantu mereka mempersiapkan diri dan mengelola perubahan.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Secara aktif menyampaikan tujuan, strategi dan status upaya perubahan; membuat rencana luas yang mendukung upaya perubahan; secara umum membantu orang lain mempersiapkan diri menghadapi perubahan..',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Secara mantap menyampaikan tujuan, strategi dan status upaya perubahan; menerjemahkan perubahan menjadi rencana tindakan spesifik; meminta pertanggungjawaban orang lain dan memahami dukungan apa yang mereka perlukan untuk mencapai target perubahan.'),
                   
                     }



###########################
##### QUESTION TO CHIEF LEVEL  #####
###########################
 
chief = {'1. Menunjukkan kesadaran diri. Menanggapi dengan pemikiran yang positif saat menghadapi tantangan atau peluang baru. Berupaya mengembangkan diri dan belajar. Mudah beradaptasi dengan berbagai cara kerja.':
                  ('(1) Melewatkan peluang untuk menerapkan pelajaran penting; puas dengan keterampilan yang ada dan kurang berusaha menerapkan saran atau kesempatan pengembangan diri baru.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Menyesuaikan pendekatan sebagaimana diperlukan untuk meraih kemajuan; ingin belajar dan bersedia memaparkan diri terhadap kesempatan pengembangan diri baru; menerapkan saran.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Memiliki pemikiran panjang saat menghadapi perubahan atau situasi bertekanan tinggi; memiliki pengaruh yang menenangkan; menyesuaikan perilaku masa depan berdasarkan saran.'),
                  
                  '2. Mendukung pertukaran informasi yang penting secara cepat dan terbuka antara diri sendiri dan orang lain di dalam perusahaan. Mendorong penyampaian ide dan pendapat secara terbuka. Menunjukkan keterampilan mendengar secara aktif. Meminta klarifikasi saat informasi atau pesan tidak jelas':
                  ('(1) Kurang menciptakan lingkungan dengan komunikasi yang terbuka dan dua-arah; kurang mendengarkan dengan baik; kurang berbagi informasi dengan pihak yang memerlukannya; tampak kesulitan dalam menyampaikan ide dan tidak diperhatikan orang.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Menciptakan komunikasi yang saling menghormati; berbagi informasi yang jelas dan dengan tingkat perincian yang tepat dengan orang yang memerlukannya, mendengarkan orang lain secara efektif.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Memastikan suasana terbuka dan mendorong komunikasi dua-arah, dengan menunjukkan minat dan empati yang tulus saat mendengarkan; berbagi informasi yang jelas pada waktu yang tepat dengan cara yang menarik, kredibel dan fasih kepada beraneka ragam orang.'),
                  
                  '3. Bertindak selaras dengan nilai Mega Perintis untuk memperoleh kepercayaan orang lain melalui etika bisnis yang baik, ketulusan dan pelaksanaan komitmen. Menunjukkan konsistensi antara perkataan dan perbuatan':
                  ('(1) Kurang memenuhi komitmen; tidak menunjukkan dukungan bagi visi, nilai dan tujuan perusahaan; kurang memperoleh penerimaan.',
                   '(2) Antara nilai 1 dan nilai 3.',
                   '(3) Membangun kepercayaan dan kredibilitas melalui perilaku yang adil, beretika; bertanggung jawab atas tindakannya; menunjukkan dukungan untuk visi, nilai dan tujuan perusahaan.',
                   '(4) Antara nilai 3 dan nilai 5.',
                   '(5) Meneladankan integritas tanpa kompromi; kepemimpinan welas asih dan tindak lanjut yang konsisten; membangkitkan dan memelihara komitmen pada visi, nilai dan tujuan perusahaan.'),
                   
                   '4. Menyuarakan dan membangkitkan komitmen pada visi dan rencana tindakan yang selaras dengan tujuan perusahaan. Menanamkan optimisme dan tanggung jawab di seluruh perusahaan, membantu orang lain membayangkan kemungkinan yang dapat dicapai':
                   ('(1) Kurang menciptakan semangat atau energi dalam perusahaan; tidak memperoleh penerimaan untuk ide, perubahan, dan inisiatif yang diajukan.',
                    '(2) Antara nilai 1 dan nilai 3.',
                    '(3) Menumbuhkan rasa semangat pada organisasi; menunjukkan keyakinan dan dasar pemikiran yang memadai saat menyajikan ide dan menanggapi reaksi; mampu membujuk para pemangku kepentingan utama untuk mendukung ide, perubahan dan inisiatif.',
                    '(4) Antara nilai 3 dan nilai 5.',
                    '(5)  Menciptakan lingkungan kerja yang menginspirasi; menyajikan ide dengan argumen bisnis yang meyakinkan; mengajukan proposal serta mengaitkannya dengan kebutuhan dan masalah orang lain.'),
                   
                   '5. Membangun hubungan dan jaringan di dalam perusahaan yang meningkatkan tingkat kerjasama, kolaborasi, dan kepercayaan di seluruh jajaran, serta dengan pelanggan dan mitra kerja, demi mewujudkan budaya yang mengutamakan perusahaan. Menangani konflik secara konstruktif dalam situasi yang sulit atau tegang.':
                   ('(1) Kurang peka, terbuka atau ramah sehingga membatasi kualitas hubungan penting dan sulit mendapat dukungan saat diperlukan; kurang mampu menghilangkan rintangan dalam kolaborasi.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Membangun jaringan hubungan dengan berinteraksi bersama orang lain secara jujur, bijak dan ramah; mendukung pola pikir yang mengutamakan kolaborasi di antara berbagai bagian perusahaan..',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Menciptakan lingkungan yang mendorong kolaborasi yang mengutamakan kepentingan perusahaan; menekankan diskusi jujur; menjalin jaringan hubungan kuat yang luas di seluruh organisasi; memiliki reputasi sebagai pemimpin yang dihormati dan ramah, serta bijak dalam berbicara.'),
                    
                    '6. Mendukung orang lain untuk memanfaatkan dan mengembangkan kemampuannya. Memberi saran dan dukungan, serta berbagi praktik terbaik. Efektif mengembangkan, mengelola, dan mempertahankan talenta penting. Mengenali dan menghargai kinerja yang baik dan membenahi masalah kinerja rendah secara konstruktif.':
                    ('(1) Kurang mendukung pembelajaran atau pengembangan diri; melewatkan peluang untuk merancang penugasan yang meningkatkan kemampuan; hanya memiliki kelompok talenta yang lemah dan sedikit jumlah suksesor yang baik.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Mendukung pengembangan dan berfokus pada para suksesor utama; memilih dan mendukung beragam individu yang bertalenta; membimbing tim dalam mempelajari kemampuan baru.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mengembangkan kelompok talenta yang kuat bagi perusahaan; menarik beragam individu yang memiliki kemampuan penting yang diperlukan; membina talenta dengan memberi bimbingan dan peran/penugasan yang menantang.'),
                    
                    '7. Memahami model bisnis Mega Perintis (industri retail), strategi dan produknya. Menyelaraskan kemampuan dengan strategi perusahaan untuk menangkap tren yang muncul, mengatasi ancaman dari pesaing, memenuhi kebutuhan pasar, memberi manfaat bagi pelanggan dan mempertahankan keunggulan kompetitif Mega Perintis.':
                    ('(1) Kurang mengidentifikasi tren pasar atau pelanggan, kurang mencari peluang baru; melewatkan peluang untuk memanfaatkan kemampuan perusahaan dan tidak meningkatkan keunggulan kompetitif perusahaan.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Menerapkan pengetahuan tentang tren pasar dan pelanggan untuk meningkatkan keunggulan kompetitif perusahaan; memanfaatkan pengetahuan ini saat membuat prasarana dan proses untuk memastikan kemampuan perusahaan yang efektif.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Memanfaatkan tren yang muncul untuk meningkatkan kesuksesan jangka panjang dan keunggulan kompetitif perusahaan; secara proaktif membangun kemampuan dan prasarana yang diperlukan untuk mendukung pertumbuhan perusahaan.'),
                    
                    '8. Menghasilkan dan memperjuangkan ide, pendekatan, solusi dan inisiatif yang baru dan inovatif. Mendukung lingkungan yang melakukan perbaikan berkelanjutan dan selalu mempertanyakan kondisi saat ini untuk meningkatkan manfaat bagi perusahaan dan pelanggan':
                    ('(1) Lebih berfokus pada jangka pendek; terlalu berhati-hati soal risiko dan melewatkan peluang untuk menerapkan pendekatan baru yang inovatif.',
                         '(2) Antara nilai 1 dan nilai 3.',
                         '(3) Menerapkan sudut pandang jangka panjang pada skala perusahaan yang mendukung inovasi dan memfokuskan karyawan pada perubahan yang akan menambah manfaat bagi perusahaan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Terus menghasilkan ide-ide inovatif untuk mengembangkan visi dan berpikiran ke depan bagi perusahaan; memanfaatkan analisis industri dan strategi bisnis untuk mendorong inovasi ke arah yang mendukung kesuksesan jangka panjang.'),
                    
                    '9. Memadukan informasi dari berbagai sumber di seluruh perusahaan untuk mengevaluasi berbagai alternatif dan mengambil keputusan efektif yang mengutamakan kepentingan perusahaan dan pelanggan. Menarik kesimpulan yang tepat dan bermanfaat dari informasi kuantitatif dan kualitatif.':
                    ('(1) Berfokus pada informasi tertentu; mengabaikan data lain untuk analisis; kesulitan mendefinisikan masalah saat berhadapan dengan data yang tidak jelas; kurang benar-benar mempertimbangkan biaya, manfaat dan risiko yang terkait dengan setiap alternatif.',
                         '(2) Antara nilai 1 dan nilai 3',
                         '(3) Menganalisis informasi sehingga menyoroti masalah utama dan implikasinya; mengambil keputusan wajar berdasarkan informasi yang tersedia, dengan mempertimbangkan biaya, risiko, dan manfaat yang relevan.',
                         '(4) Antara nilai 3 dan nilai 5.',
                         '(5) Mengintegrasikan informasi kompleks; jelas mendefinisikan semua masalah, akar penyebab dan kemungkinan implikasinya; memanfaatkan informasi kuantitatif dan keuangan yang tersedia secara maksimal untuk menghasilkan keputusan dan solusi terbaik.'),
                    
                    '10. Mengembangkan solusi yang mengutamakan pelanggan. Menyediakan pengalaman, produk dan layanan yang memenuhi atau melebihi persyaratan pelanggan (internal dan eksternal). Terus-menerus mengidentifikasi dan membuat cara baru untuk meningkatkan kepuasan dan kesetiaan pelanggan serta memastikan masalah pelanggan dapat diatasi.':
                    ('(1) Hanya berfokus pada layanan, kurang mencari saran atau menjelajahi tren dalam industri; melewatkan peluang untuk menyingkirkan rintangan dalam layanan atau menerapkan perubahan yang meningkatkan pengalaman pelanggan..',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Menekankan layanan dan sangat perlunya memahami pelanggan dan kebutuhan mereka; menerapkan saran dan informasi tren untuk merancang dan menyempurnakan solusi dan pendekatan pada pelanggan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Memastikan perusahaan yang fokus untuk menciptakan layanan pelanggan yang memuaskan; memanfaatkan tren untuk menyingkirkan rintangan terhadap layanan; menerapkan solusi dan pendekatan baru yang meningkatkan pengalaman pelanggan.'),
                    
                    '11. Memfokuskan, menyelaraskan dan mengoptimalkan penggunaan sumber daya untuk mencapai tujuan. Menunjukkan prioritas, mengelola kinerja, menuntut tanggung jawab diri sendiri dan orang lain dalam menyelesaikan pekerjaan dan menyingkirkan rintangan secara efektif dan efisien demi meraih sukses.':
                   ('(1) Kurang bisa menerjemahkan tujuan strategis menjadi tindakan yang konkret dan terukur; kurang mampu mengatur koordinasi yang baik atau menyusun rencana cadangan untuk mengantisipasi risiko; kesulitan menuntaskan masalah.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Menerjemahkan tujuan strategis menjadi tujuan dan rencana tindakan spesifik; menetapkan tujuan yang menantang tapi realistis; menunjukkan kepekaan mengenai skala prioritas; meraih tujuan dengan standar kinerja tinggi dan berupaya menuntaskan masalah..',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Selalu menyusun dan menentukan strategi dengan mengidentifikasi tujuan dan rencana tindakan yang agresif dan konkret; mengintegrasikan upaya perencanaan di seluruh perusahaan untuk memastikan tercapainya tujuan strategis; selalu menekankan pentingnya menuntaskan persoalan.'),
                    
                    '12. Mengelola perubahan agar perusahaan mencapai sukses. Bekerja secara produktif saat menghadapi ketidakjelasan atau ketidakpastian. Membantu orang lain menyambut perubahan secara positif.':
                    ('(1) Menerapkan inisiatif perubahan tanpa mempertimbangkan terjaganya keefektifan operasional; kurang berminat mempertanyakan kondisi saat ini; hampir tidak melakukan apa pun untuk menanggapi ancaman, peluang dan tren di lingkungan luar.',
                          '(2) Antara nilai 1 dan nilai 3.',
                          '(3) Menerapkan inisiatif perubahan dengan minimal gangguan pada keefektifan operasi; berupaya menyajikan visi perubahan yang meyakinkan; menilai ancaman, peluang, dan tren untuk memahami perubahan yang diperlukan demi kesuksesan perusahaan.',
                          '(4) Antara nilai 3 dan nilai 5.',
                          '(5) Mengelola perubahan untuk menjaga keefektifan operasional; menyajikan visi dan argumen meyakinkan tentang perubahan yang mendorong komitmen besar dari pemangku kepentingan; secara proaktif menilai ancaman, peluang dan tren untuk mendorong terobosan perubahan.'),
                   
                     }


###########################
##### FORM QUESTION  #####
###########################

with c2:
    with st.form('form_2'):
        
        
        ###########################
        ##### FORMAT DATABASE NYA #####
        ########################### 
        
        ## sesuai form 1 
        ## save record data to dataframe
        save_data['Time Stamp'] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now(tz = pytz.timezone('Asia/Jakarta')))
        save_data['Nama Penilai'] = st.session_state['cari_1']
        save_data['NIK Nama Penilai'] = str(nik_eval)
        
        save_data['Nama Yang Akan Dinilai'] = search_2.split('*')[1]
        #save_data['NIK nama yang akan nilai'] = search_2.split('*')[3]
        save_data['Jabatan'] = search_2.split('*')[5]
        save_data['Divisi'] = search_2.split('*')[7]
        save_data['Hubungan'] = search_2.split('*')[9]
        
        
        ###########################
        ##### AUTO LOGIC UNTUK LEVEL #####
        ###########################
        
        # question for staff 
        if 'Staff' in search_2.split('*')[5]:
            st.title('Evaluasi Kompetensi untuk Staff')
            st.markdown('')
            st.markdown('')
            
            save_data['Leadership Level'] = 'Staff'
           
            # for time stamp 

            ### for question 1
            st.header('Membangun Integritas Pribadi - ***SPIRIT***')
            st.subheader("1. Tanggung Jawab Pribadi")
            # for question moment 
            st.write(tuple(staff_question.items())[0][0])
            
            # for answer moment 
            
            radio_1 = st.radio('select here!', tuple(staff_question.values())[0])
            
            save_data['Tanggung Jawab Pribadi'] = radio_1.split(' ')[0].strip('()')
             
            
            st.caption('Wajib di isi')
            
            
            ### for question two
            st.subheader("2. Komunikasi Efektif")
            # for question moment 
             
            st.write(tuple(staff_question.items())[1][0])
            
            # for answer moment 
            radio_2 = st.radio('select here!', tuple(staff_question.values())[1])
            
            save_data['Komunikasi Efektif'] = radio_2.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 3
            
            st.subheader("3. Membangun Kepercayaan")
            # for question moment 
            
            st.write(tuple(staff_question.items())[2][0])
            
            # for answer moment 
            radio_3 = st.radio('select here!', tuple(staff_question.values())[2])
            
            save_data['Membangun Kepercayaan'] = radio_3.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
             # for question 4
            st.header('Bekerja untuk Kita Semua - ***WE WORK FOR US***')
            st.subheader("1. Melibatkan dan Mempengaruhi")
            # for question moment 
            
            st.write(tuple(staff_question.items())[3][0])
            
            # for answer moment 
            radio_4 = st.radio('select here!', tuple(staff_question.values())[3])
            
            save_data['Melibatkan dan Mempengaruhi'] = radio_4.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 5
            ## nanti lanjut disini dengan format yang sama 
            st.subheader("2. Kolaborasi dan Kerjasama")
            # for question moment 
            st.write(tuple(staff_question.items())[4][0])
            
            # for answer moment 
            radio_5 = st.radio('select here!', tuple(staff_question.values())[4])
            
            save_data['Kolaborasi dan Kerjasama'] = radio_5.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            ## for question enam
            st.subheader("3. Menumbuhkan Talenta Organisasi")
            # for question moment 
            st.write(tuple(staff_question.items())[5][0])
            
            # for answer moment 
            radio_6 = st.radio('select here!', tuple(staff_question.values())[5])
            
            save_data['Menumbuhkan Talenta Organisasi'] = radio_6.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question tujuh 
            st.header('Berinovasi untuk Menang - ***LOVE OUR BRAND***')
            st.subheader("1. Kepiawaian Bisnis")
            # for question moment 
            st.write(tuple(staff_question.items())[6][0])
            
            # for answer moment 
            radio_7 = st.radio('select here!', tuple(staff_question.values())[6])
            
            save_data['Kepiawaian Bisnis'] = radio_7.split(' ')[0].strip('()')
           
            st.caption('Wajib di isi')
                         
            # for question delapan
            st.subheader("2. Inovasi dan Terus Meningkat")
            # for question moment 
            st.write(tuple(staff_question.items())[7][0])
            
            # for answer moment 
            radio_8 = st.radio('select here!', tuple(staff_question.values())[7])
            
            save_data['Inovasi dan Terus Meningkat'] = radio_8.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
                         
            # for question 9
            st.subheader("3. Pengambilan Keputusan")
            # for question moment 
            st.write(tuple(staff_question.items())[8][0])
            
            # for answer moment 
            radio_9 = st.radio('select here!', tuple(staff_question.values())[8])
            
            save_data['Pengambil Keputusan'] = radio_9.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                     
                         
             # for question 10
            st.header('Fokus pada Pelanggan - ***HAPPY CUSTOMER***')
            st.subheader("Fokus Kepada Pelanggan")
            # for question moment 
            st.write(tuple(staff_question.items())[9][0])
            
            # for answer moment 
            radio_10 = st.radio('select here!', tuple(staff_question.values())[9])
            
            save_data['Fokus Kepada Pelanggan'] = radio_10.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                     
            # for question 11
            st.subheader("2. Perancanaan dan Pelaksanaan")
            # for question moment 
            st.write(tuple(staff_question.items())[10][0])
            
            # for answer moment 
            radio_11 = st.radio('select here!', tuple(staff_question.values())[10])
            
            save_data['Perencanaan dan Pelaksanaan'] = radio_11.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                
            # for question 12
            st.subheader("3. Mengelola Perubahan")
            # for question moment 
            st.write(tuple(staff_question.items())[11][0])
            
            # for answer moment 
            radio_12 = st.radio('select here!', tuple(staff_question.values())[11])
            
            save_data['Mengelola Perubahan'] = radio_12.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 13 
            st.header('Saran dari Penilai')
                         
            max_words = 1000
            import re
            saran = st.text_area('Masukan Saran disini, ya!!', height = 200, help = 'maximal 1000 kata')
            res = len(re.findall(r'\w+', saran))
            if res > max_words:
                st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 1000 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )
            
            save_data['Saran'] = saran 
            
        
        
        
        # question for section dan officer 
        elif 'Officer' in search_2.split('*')[5]:
            st.title('Evaluasi Kompetensi untuk Section/Officer')
            st.markdown('')
            st.markdown('')
            
            save_data['Leadership Level'] = 'Sect. Head'
           
            ### for question 1
            
            st.header('Membangun Integritas Pribadi - ***SPIRIT***')
            
            st.subheader("1. Tanggung Jawab Pribadi")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[0][0])
            
            # for answer moment 
            radio_13 = st.radio('select here!', tuple(staff_section_dan_officer.values())[0])
            
            save_data["Tanggung Jawab Pribadi"] = radio_13.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            

            ### for question two
            st.subheader("2. Komunikasi Efektif")
            # for question moment 
             
            st.write(tuple(staff_section_dan_officer.items())[1][0])
            
            # for answer moment 
            radio_14 = st.radio('select here!', tuple(staff_section_dan_officer.values())[1])
            
            save_data['Komunikasi Efektif'] = radio_14.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 3
            
            st.subheader("3. Membangun Kepercayaan ")
            # for question moment 
            
            st.write(tuple(staff_section_dan_officer.items())[2][0])
            
            # for answer moment 
            radio_15 = st.radio('select here!', tuple(staff_section_dan_officer.values())[2])
            
            save_data['Membangun Kepercayaan'] = radio_15.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            
             # for question 4
            st.header('Bekerja Untuk Kita Semua - ***WE WORK FOR US***')
            
            st.subheader("1. Melibatkan dan Mempengaruhi")
            # for question moment 
            
            st.write(tuple(staff_section_dan_officer.items())[3][0])
            
            # for answer moment 
            radio_16 = st.radio('select here!', tuple(staff_section_dan_officer.values())[3])
            
            save_data['Melibatkan dan Mempengaruhi'] = radio_16.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 5
            ## nanti lanjut disini dengan format yang sama 
            st.subheader("2. Kolaborasi dan Kerjasama")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[4][0])
            
            # for answer moment 
            radio_17 = st.radio('select here!', tuple(staff_section_dan_officer.values())[4])
            
            save_data['Kolaborasi dan Kerjasama'] = radio_17.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            ## for question enam
            st.subheader("3. Menumbuhkan Talenta Organisasi")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[5][0])
            
            # for answer moment 
            radio_18 = st.radio('select here!', tuple(staff_section_dan_officer.values())[5])
            
            save_data["Menumbuhkan Talenta Organisasi"] = radio_18.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            st.header('Berinovasi untuk Menang - ***LOVE OUR BRAND***')
            
            # for question tujuh 
            st.subheader("1. Kepiawaian Bisnis")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[6][0])
            
            # for answer moment 
            radio_19 = st.radio('select here!', tuple(staff_section_dan_officer.values())[6])
            
            save_data['Kepiawaian Bisnis'] = radio_19.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
            # for question delapan
            st.subheader("2. Inovasi dan Terus Meningkatkan")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[7][0])
            
            # for answer moment 
            radio_20 = st.radio('select here!', tuple(staff_section_dan_officer.values())[7])
            
            save_data['Inovasi dan Terus Meningkatkan'] = radio_20.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
                         
            # for question 9
            st.subheader("3. Pengambil Keputusan")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[8][0])
            
            # for answer moment 
            radio_21 = st.radio('select here!', tuple(staff_section_dan_officer.values())[8])
            
            save_data['Pengambilan Keputusan'] = radio_21.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                     
            
            st.header('Fokus pada Pelanggan - ***HAPPY CUSTOMER***')
             # for question 10
            st.subheader("1. Fokus Kepada Pelanggan")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[9][0])
            
            # for answer moment 
            radio_22 = st.radio('select here!', tuple(staff_section_dan_officer.values())[9])
            
            save_data['Fokus Kepada Pelanggan'] = radio_22.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                     
            # for question 11
            st.subheader("2. Perencanaan dan Pelaksanaan")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[10][0])
            
            # for answer moment 
            radio_23 = st.radio('select here!', tuple(staff_section_dan_officer.values())[10])
            
            save_data['Perencanaan dan Pelaksanaan'] = radio_23.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                
            # for question 12
            st.subheader("3. Mengelola Perubahan")
            # for question moment 
            st.write(tuple(staff_section_dan_officer.items())[11][0])
            
            # for answer moment 
            radio_24 = st.radio('select here!', tuple(staff_section_dan_officer.values())[11])
            
            save_data['Mengelola Perubahan'] = radio_24.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 13 
            st.header('Saran dari Penilai')
                         
            max_words = 1000
            import re
            saran_1 = st.text_area('Masukan Saran disini, ya!!', height = 200, help = 'maximal 1000 kata')
            res_1 = len(re.findall(r'\w+', saran_1))
            if res_1 > max_words:
                st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 1000 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )
            save_data['Saran'] = saran_1 
        
        
        # question for division head
        elif 'Division Head' in search_2.split('*')[5]:
            st.title('Evaluasi Kompetensi untuk Division Head')
            st.markdown('')
            st.markdown('')
            
            save_data['Leadership Level'] = 'Div. Head'
            
            ### for question 1
            
            st.header('Membangun Integritas Pribadi - ***SPIRIT***')
            
            st.subheader("1. Tanggung Jawab Pribadi")
            # for question moment 
            st.write(tuple(division_head.items())[0][0])
            
            # for answer moment 
            radio_25 = st.radio('select here!', tuple(division_head.values())[0])
            
            save_data['Tanggung Jawab Pribadi'] = radio_25.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            

            ### for question two
            st.subheader("2. Komunikasi Efektif")
            # for question moment 
             
            st.write(tuple(division_head.items())[1][0])
            
            # for answer moment 
            radio_26 = st.radio('select here!', tuple(division_head.values())[1])
            
            save_data['Komunikasi Efektif'] = radio_26.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 3
            
            st.subheader("3. Membangun Kepercayaan")
            # for question moment 
            
            st.write(tuple(division_head.items())[2][0])
            
            # for answer moment 
            radio_27 = st.radio('select here!', tuple(division_head.values())[2])
            
            save_data['Membangun Kepercayaan'] = radio_27.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            
             # for question 4
            st.header('Bekerja Untuk Kita Semua - ***WE WORK FOR US***')
            
            st.subheader("1. Melibatkan dan Mempengaruhi")
            # for question moment 
            
            st.write(tuple(division_head.items())[3][0])
            
            # for answer moment 
            radio_28 = st.radio('select here!', tuple(division_head.values())[3])
            
            save_data['Melibatkan dan Mempengaruhi'] = radio_28.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 5
            ## nanti lanjut disini dengan format yang sama 
            st.subheader("2. Kolaborasi dan Kerjasama")
            # for question moment 
            st.write(tuple(division_head.items())[4][0])
            
            # for answer moment 
            radio_29 = st.radio('select here!', tuple(division_head.values())[4])
            
            save_data['Kolaborasi dan Kerjasama'] = radio_29.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            ## for question enam
            st.subheader("3. Menumbuhkan Talenta Organisasi")
            # for question moment 
            st.write(tuple(division_head.items())[5][0])
            
            # for answer moment 
            radio_30 = st.radio('select here!', tuple(division_head.values())[5])
            
            save_data['Menumbuhkan Talenta Organisasi'] = radio_30.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            st.header('Berinovasi untuk Menang - ***LOVE OUR BRAND***')
            
            # for question tujuh 
            st.subheader("1. Kepiawaian Bisnis")
            # for question moment 
            st.write(tuple(division_head.items())[6][0])
            
            # for answer moment 
            radio_31 = st.radio('select here!', tuple(division_head.values())[6])
            
            save_data['Kepiawaian Bisnis'] = radio_31.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
            # for question delapan
            st.subheader("2. Inovasi dan Terus Meningkatkan")
            # for question moment 
            st.write(tuple(division_head.items())[7][0])
            
            # for answer moment 
            radio_32 = st.radio('select here!', tuple(division_head.values())[7])
            
            save_data['Inovasi dan Terus Meningkatkan'] = radio_32.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
                         
            # for question 9
            st.subheader("3. Pengambil Keputusan")
            # for question moment 
            st.write(tuple(division_head.items())[8][0])
            
            # for answer moment 
            radio_33 = st.radio('select here!', tuple(division_head.values())[8])
            
            save_data['Pengambil Keputusan'] = radio_33.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                     
            
            st.header('Fokus pada Pelanggan - ***HAPPY CUSTOMER***')
             # for question 10
            st.subheader("1. Fokus Kepada Pelanggan")
            # for question moment 
            st.write(tuple(division_head.items())[9][0])
            
            # for answer moment 
            radio_34 = st.radio('select here!', tuple(division_head.values())[9])
            
            save_data['Fokus Kepada Pelanggan'] = radio_34.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                     
            # for question 11
            st.subheader("2. Perencanaan dan Pelaksanaan")
            # for question moment 
            st.write(tuple(division_head.items())[10][0])
            
            # for answer moment 
            radio_35 = st.radio('select here!', tuple(division_head.values())[10])
            
            save_data['Perencanaan dan Pelaksanaan'] = radio_35.split(' ')[0].strip('()')
        
            st.caption('Wajib di isi')
                         
                
            # for question 12
            st.subheader("3. Mengelola Perubahan")
            # for question moment 
            st.write(tuple(division_head.items())[11][0])
            
            # for answer moment 
            radio_36 = st.radio('select here!', tuple(division_head.values())[11])
            
            save_data['Mengelola Perubahan'] = radio_36.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 13 
            st.header('Saran dari Penilai')
                         
            max_words = 1000
            import re
            saran_2 = st.text_area('Masukan Saran disini, ya!!', height = 200, help = 'maximal 1000 kata')
            res_2 = len(re.findall(r'\w+', saran_2))
            if res_2 > max_words:
                st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 1000 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )
            save_data['Saran'] = saran_2
           
            
            
          # question for dept head
        elif 'Dept Head' in search_2.split('*')[5]:
            st.title('Evaluasi Kompetensi untuk Department Head (Manager)')
            st.markdown('')
            st.markdown('')
            
            save_data['Leadership Level'] = 'Dept. Head'
            
            ### for question 1
            
            st.header('Membangun Integritas Pribadi - ***SPIRIT***')
            
            st.subheader("1. Tanggung Jawab Pribadi")
            # for question moment 
            st.write(tuple(department_head.items())[0][0])
            
            # for answer moment 
            radio_37 = st.radio('select here!', tuple(department_head.values())[0])
            
            save_data['Tanggung Jawab Pribadi'] = radio_37.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            

            ### for question two
            st.subheader("2. Komunikasi Efektif")
            # for question moment 
             
            st.write(tuple(department_head.items())[1][0])
            
            # for answer moment 
            radio_38 = st.radio('select here!', tuple(department_head.values())[1])
            
            save_data['Komunikasi Efektif'] = radio_38.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 3
            
            st.subheader("3. Membangun Kepercayaan ")
            # for question moment 
            
            st.write(tuple(department_head.items())[2][0])
            
            # for answer moment 
            radio_39 = st.radio('select here!', tuple(department_head.values())[2])
            
            save_data['Membangun Kepercayaan'] = radio_39.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            
             # for question 4
            st.header('Bekerja Untuk Kita Semua - ***WE WORK FOR US***')
            
            st.subheader("1. Melibatkan dan Mempengaruhi")
            # for question moment 
            
            st.write(tuple(department_head.items())[3][0])
            
            # for answer moment 
            radio_40 = st.radio('select here!', tuple(department_head.values())[3])
            
            save_data['Melibatkan dan Mempengaruhi'] = radio_40.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 5
            ## nanti lanjut disini dengan format yang sama 
            st.subheader("2. Kolaborasi dan Kerjasama")
            # for question moment 
            st.write(tuple(department_head.items())[4][0])
            
            # for answer moment 
            radio_41 = st.radio('select here!', tuple(department_head.values())[4])
            
            save_data['Kolaborasi dan Kerjasama'] = radio_41.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            ## for question enam
            st.subheader("3. Menumbuhkan Talenta Organisasi")
            # for question moment 
            st.write(tuple(department_head.items())[5][0])
            
            # for answer moment 
            radio_42 = st.radio('select here!', tuple(department_head.values())[5])
            
            save_data['Menumbuhkan Talenta Organisasi'] = radio_42.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            st.header('Berinovasi untuk Menang - ***LOVE OUR BRAND***')
            
            # for question tujuh 
            st.subheader("1. Kepiawaian Bisnis")
            # for question moment 
            st.write(tuple(department_head.items())[6][0])
            
            # for answer moment 
            radio_43 = st.radio('select here!', tuple(department_head.values())[6])
            
            save_data['Kepiawaian Bisnis'] = radio_43.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
            # for question delapan
            st.subheader("2. Inovasi dan Terus Meningkatkan")
            # for question moment 
            st.write(tuple(department_head.items())[7][0])
            
            # for answer moment 
            radio_44 = st.radio('select here!', tuple(department_head.values())[7])
            
            save_data['Inovasi dan Terus Meningkatkan'] = radio_44.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
                         
            # for question 9
            st.subheader("3. Pengambil Keputusan")
            # for question moment 
            st.write(tuple(department_head.items())[8][0])
            
            # for answer moment 
            radio_45 = st.radio('select here!', tuple(department_head.values())[8])
            
            save_data['Pengambil Keputusan'] = radio_45.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                     
            
            st.header('Fokus pada Pelanggan - ***HAPPY CUSTOMER***')
             # for question 10
            st.subheader("1. Fokus Kepada Pelanggan")
            # for question moment 
            st.write(tuple(department_head.items())[9][0])
            
            # for answer moment 
            radio_46 = st.radio('select here!', tuple(department_head.values())[9])
            
            save_data['Fokus Kepada Pelanggan'] = radio_46.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                     
            # for question 11
            st.subheader("2. Perencanaan dan Pelaksanaan")
            # for question moment 
            st.write(tuple(department_head.items())[10][0])
            
            # for answer moment 
            radio_47 = st.radio('select here!', tuple(department_head.values())[10])
            
            save_data['Perencanaan dan Pelaksanaan'] = radio_47.split(' ')[0].strip('()')
        
            st.caption('Wajib di isi')
                         
                
            # for question 12
            st.subheader("3. Mengelola Perubahan")
            # for question moment 
            st.write(tuple(department_head.items())[11][0])
            
            # for answer moment 
            radio_48 = st.radio('select here!', tuple(department_head.values())[11])
            
            save_data['Mengelola Perubahan'] = radio_48.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 13 
            st.header('Saran dari Penilai')
                         
            max_words = 1000
            import re
            saran_3 = st.text_area('Masukan Saran disini, ya!!', height = 200, help = 'maximal 1000 kata')
            res_3 = len(re.findall(r'\w+', saran_3))
            if res_3 > max_words:
                st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 1000 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )
            save_data['Saran'] = saran_3
            
        
        # question for chief 
        elif 'Chief' in search_2.split('*')[5] or 'Director' in search_2.split('*')[5]:
            st.title('Evaluasi Kompetensi untuk Chief Officer')
            st.markdown('')
            st.markdown('')
            
            save_data['Leadership Level'] = 'Chief'
            
           
            ### for question 1
            
            st.header('Membangun Integritas Pribadi - ***SPIRIT***')
            
            st.subheader("1. Tanggung Jawab Pribadi")
            # for question moment 
            st.write(tuple(chief.items())[0][0])
            
            # for answer moment 
            radio_49 = st.radio('select here!', tuple(chief.values())[0])
            
            save_data['Tanggung Jawab Pribadi'] = radio_49.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            

            ### for question two
            st.subheader("2. Komunikasi Efektif")
            # for question moment 
             
            st.write(tuple(chief.items())[1][0])
            
            # for answer moment 
            radio_50 = st.radio('select here!', tuple(chief.values())[1])
            
            save_data["Komunikasi Efektif"] = radio_50.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 3
            
            st.subheader("3. Membangun Kepercayaan ")
            # for question moment 
            
            st.write(tuple(chief.items())[2][0])
            
            # for answer moment 
            radio_51 = st.radio('select here!', tuple(chief.values())[2])
            
            save_data['Membangun Kepercayaan'] = radio_51.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            
             # for question 4
            st.header('Bekerja Untuk Kita Semua - ***WE WORK FOR US***')
            
            st.subheader("1. Melibatkan dan Mempengaruhi")
            # for question moment 
            
            st.write(tuple(chief.items())[3][0])
            
            # for answer moment 
            radio_52 = st.radio('select here!', tuple(chief.values())[3])
            
            save_data['Melibatkan dan Mempengaruhi'] = radio_52.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 5
            ## nanti lanjut disini dengan format yang sama 
            st.subheader("2. Kolaborasi dan Kerjasama")
            # for question moment 
            st.write(tuple(chief.items())[4][0])
            
            # for answer moment 
            radio_53 = st.radio('select here!', tuple(chief.values())[4])
            
            save_data['Kolaborasi dan Kerjasama'] = radio_53.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            ## for question enam
            st.subheader("3. Menumbuhkan Talenta Organisasi")
            # for question moment 
            st.write(tuple(chief.items())[5][0])
            
            # for answer moment 
            radio_54 = st.radio('select here!', tuple(chief.values())[5])
            
            save_data['Menumbuhkan Talenta Organisasi'] = radio_54.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            st.header('Berinovasi untuk Menang - ***LOVE OUR BRAND***')
            
            # for question tujuh 
            st.subheader("1. Kepiawaian Bisnis")
            # for question moment 
            st.write(tuple(chief.items())[6][0])
            
            # for answer moment 
            radio_55 = st.radio('select here!', tuple(chief.values())[6])
            
            save_data['Kepiawaian Bisnis'] = radio_55.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
            # for question delapan
            st.subheader("2. Inovasi dan Terus Meningkatkan")
            # for question moment 
            st.write(tuple(chief.items())[7][0])
            
            # for answer moment 
            radio_56 = st.radio('select here!', tuple(chief.values())[7])
            
            save_data['Inovasi dan Terus Meningkatkan'] = radio_56.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
                         
            # for question 9
            st.subheader("3. Pengambil Keputusan")
            # for question moment 
            st.write(tuple(chief.items())[8][0])
            
            # for answer moment 
            radio_57 = st.radio('select here!', tuple(chief.values())[8])
            
            save_data['Pengambil Keputusan'] = radio_57.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                     
            
            st.header('Fokus pada Pelanggan - ***HAPPY CUSTOMER***')
             # for question 10
            st.subheader("1. Fokus Kepada Pelanggan")
            # for question moment 
            st.write(tuple(chief.items())[9][0])
            
            # for answer moment 
            radio_58 = st.radio('select here!', tuple(chief.values())[9])
            
            save_data['Fokus Kepada Pelanggan'] = radio_58.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
                         
                     
            # for question 11
            st.subheader("2. Perencanaan dan Pelaksanaan")
            # for question moment 
            st.write(tuple(chief.items())[10][0])
            
            # for answer moment 
            radio_59 = st.radio('select here!', tuple(chief.values())[10])
            
            save_data['Perencanaan dan Pelaksanaan'] = radio_59.split(' ')[0].strip('()')
        
            st.caption('Wajib di isi')
                         
                
            # for question 12
            st.subheader("3. Mengelola Perubahan")
            # for question moment 
            st.write(tuple(chief.items())[11][0])
            
            # for answer moment 
            radio_60 = st.radio('select here!', tuple(chief.values())[11])
            
            save_data['Mengelola Perubahan'] = radio_60.split(' ')[0].strip('()')
            
            st.caption('Wajib di isi')
            
            
            # for question 13 
            st.header('Saran dari Penilai')
                         
            max_words = 1000
            import re
            saran_4 = st.text_area('Masukan Saran disini, ya!!', height = 200, help = 'maximal 1000 kata')
            res_4 = len(re.findall(r'\w+', saran_4))
            if res_4 > max_words:
                st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 1000 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )
            save_data['Saran'] = saran_4
            
            
            
        ###########################
        ##### SUBMIT PENILAIAN MOMENT #####
        ########################### 
        
        ## ini nanti 
        # st.caption('Sudah otomatis')

        st.header('Hasil Penilaian anda')
        
        # DETAIL NYA
        st.markdown('Note: Penilai ***' + st.session_state['cari_1'] + '*** & ' + 'NIK ' + '***' + str(nik_eval) + '***' + ' Nama Yang akan di nilai ' +'***' + search_2 + '***.')
        save_data['Detail'] =  'Penilai ' + st.session_state['cari_1'] + ' Nama Yang akan di nilai ' + search_2
            
            
        # store to dataframe
        st.caption(f'berikut hasil penilaian dari rekan - rekan **{st.session_state["cari_1"]}**')
        #to_df = pd.DataFrame([save_data])
        #st.dataframe(to_df[['Time Stamp', 'Nama Penilai', 'NIK Nama Penilai', 'Nama Yang Akan Dinilai', 'Detail']])
        
        # get latest respon # only for atasan
        show_df = data_latest[data_latest['Nama Yang Akan Dinilai'] == st.session_state['cari_1']].drop_duplicates(subset = 'Nama Penilai').fillna('None').reset_index(drop = True)
        st.dataframe(show_df)
        
        #st.caption('di atas ini adalah format detail data hasil penilaian & data langsung tersimpan di database, jika sudah submit')
        b5 = st.checkbox('⚠️ apakah anda yakin?', help = 'klik ini untuk menyimpan')
        st.caption('wajib di klik untuk menyimpan')
        
        
        ## TO CONNECT TO GSHEET WITH GCP API 

        # CONNECT WITH API 
        gc = gspread.service_account(filename="mp-evaluator-359610-b73f5a8737fb.json")

        # OPEN data output
        sh = gc.open_by_key("1xNy6XktUGcUEZJj3EMGTFa9gFIQ0JyrTOZ8zpb5eKBU")
        # select sheet 
        worksheet = sh.worksheet('RESPON_2')
        #### conenct api end 

        ## to submit and save to gsheet 
        
        b4 = st.form_submit_button('Submit dan save 💾', help = 'pastikan tombol checkbox yang di atas di klik untuk menyimpan')
        
        # cta save 
        if b4 and b5:
            # with c92:
                # FIRST UPDATE WITH NEW FORMAT 
            with st.spinner('Mohon Bersabar sedang loading'):
                time.sleep(random.choice([2,3,4]))
            #worksheet.update([to_df.columns.values.tolist()] + to_df.values.tolist()) # < this for update new format
            worksheet.append_rows(to_df.values.tolist()) # this for append while clik submit 

            st.success('Selamat Penilaian anda berhasil tersimpan, Terima kasih atas penilaian anda', icon="✅")

                



## matikan streamlit nya
hide_menu_style = """
        <style>
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

## for ui 00AA13
