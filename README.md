# Fitur
Input: Deskripsi teks dalam bahasa Indonesia
Output: File DXF dan SVG yang siap diimpor ke software CAD
Objek yang didukung: Kursi dan Ruangan
Format output: DXF (AutoCAD) dan SVG (vector graphic)
Testing otomatis: 4 test case included

# Contoh Input yang Didukung
# Untuk Kursi:

  Kursi dengan 4 kaki, dudukan persegi 40x40 cm, tinggi 45 cm

# Untuk Ruangan:

  Ruangan ukuran 4x5 meter, dengan 1 pintu di sisi barat dan 1 jendela di sisi utara

# Output:
hasil.dxf → file DXF

hasil.svg → file SVG

test_1.dxf, test_1.svg, … test_4.svg → file hasil uji otomatis

#Asumsi dan Simplifikasi:

Kursi: Kaki direpresentasikan sebagai lingkaran kecil di sudut

Pintu: Menggunakan simbol garis dengan arc bukaan 90 derajat

Jendela: Garis tunggal dengan panjang 15 unit

Ruangan: Skala 1:100 (meter ke cm)

#Library yang Digunakan:

ezdxf untuk generasi file DXF

svgwrite untuk generasi file SVG

re untuk parsing teks dengan regular expression


