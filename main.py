import re
import ezdxf
import svgwrite

def parse_description(text):
    """Parse deskripsi teks sederhana menjadi objek geometris."""
    text = text.lower()
    objects = {}

    # Deteksi kursi
    if "kursi" in text:
        ukuran = re.search(r"(\d+)\s*x\s*(\d+)\s*cm", text)
        tinggi = re.search(r"tinggi\s*(\d+)\s*cm", text)
        if ukuran and tinggi:
            panjang = int(ukuran.group(1))
            lebar = int(ukuran.group(2))
            tinggi = int(tinggi.group(1))
            objects["kursi"] = {"panjang": panjang, "lebar": lebar, "tinggi": tinggi}

    # Deteksi ruangan
    if "ruangan" in text:
        ukuran = re.search(r"(\d+)\s*x\s*(\d+)\s*meter", text)
        pintu = re.search(r"pintu.*?(barat|timur|utara|selatan)", text)
        jendela = re.search(r"jendela.*?(barat|timur|utara|selatan)", text)
        if ukuran:
            panjang = int(ukuran.group(1)) * 100  # meter ke cm
            lebar = int(ukuran.group(2)) * 100
            objects["ruangan"] = {
                "panjang": panjang,
                "lebar": lebar,
                "pintu": pintu.group(1) if pintu else None,
                "jendela": jendela.group(1) if jendela else None,
            }

    return objects

def draw_dxf(objects, filename="hasil.dxf"):
    """Buat file DXF dari objek dengan koordinat yang benar."""
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    
    y_offset = 0  # Untuk menumpuk gambar vertikal
    
    for obj, props in objects.items():
        if obj == "kursi":
            # Tampak atas - kursi
            msp.add_lwpolyline([
                (0, y_offset), 
                (props["panjang"], y_offset),
                (props["panjang"], y_offset + props["lebar"]), 
                (0, y_offset + props["lebar"]), 
                (0, y_offset)
            ])
            
            # Kaki kursi (tampak atas)
            kaki_radius = 2
            msp.add_circle((5, y_offset + 5), kaki_radius)
            msp.add_circle((props["panjang"] - 5, y_offset + 5), kaki_radius)
            msp.add_circle((5, y_offset + props["lebar"] - 5), kaki_radius)
            msp.add_circle((props["panjang"] - 5, y_offset + props["lebar"] - 5), kaki_radius)
            
            # Tampak depan - kursi (ditempatkan di samping)
            x_offset_front = props["panjang"] + 50
            msp.add_lwpolyline([
                (x_offset_front, y_offset),
                (x_offset_front + props["panjang"], y_offset),
                (x_offset_front + props["panjang"], y_offset + props["tinggi"]),
                (x_offset_front, y_offset + props["tinggi"]),
                (x_offset_front, y_offset)
            ])
            
            y_offset += max(props["lebar"], props["tinggi"]) + 50
            
        elif obj == "ruangan":
            # Tampak atas - ruangan
            room_x, room_y = 0, y_offset
            room_width, room_height = props["panjang"], props["lebar"]
            
            msp.add_lwpolyline([
                (room_x, room_y),
                (room_x + room_width, room_y),
                (room_x + room_width, room_y + room_height),
                (room_x, room_y + room_height),
                (room_x, room_y)
            ])
            
            # Pintu
            door_width = 20
            if props["pintu"] == "barat":  # sisi kiri
                door_y = room_y + room_height/2 - door_width/2
                msp.add_line((room_x, door_y), (room_x, door_y + door_width))
                # Tanda bukaan pintu
                msp.add_arc((room_x, door_y + door_width/2), 10, 0, 90)
                
            elif props["pintu"] == "timur":  # sisi kanan
                door_y = room_y + room_height/2 - door_width/2
                msp.add_line((room_x + room_width, door_y), (room_x + room_width, door_y + door_width))
                msp.add_arc((room_x + room_width, door_y + door_width/2), 10, 90, 180)
                
            elif props["pintu"] == "utara":  # sisi atas
                door_x = room_x + room_width/2 - door_width/2
                msp.add_line((door_x, room_y + room_height), (door_x + door_width, room_y + room_height))
                msp.add_arc((door_x + door_width/2, room_y + room_height), 10, 180, 270)
                
            elif props["pintu"] == "selatan":  # sisi bawah
                door_x = room_x + room_width/2 - door_width/2
                msp.add_line((door_x, room_y), (door_x + door_width, room_y))
                msp.add_arc((door_x + door_width/2, room_y), 10, 270, 360)
            
            # Jendela
            window_size = 15
            if props["jendela"] == "barat":  # sisi kiri
                window_y = room_y + room_height/3
                msp.add_line((room_x, window_y), (room_x, window_y + window_size))
                
            elif props["jendela"] == "timur":  # sisi kanan
                window_y = room_y + room_height/3
                msp.add_line((room_x + room_width, window_y), (room_x + room_width, window_y + window_size))
                
            elif props["jendela"] == "utara":  # sisi atas
                window_x = room_x + room_width/3
                msp.add_line((window_x, room_y + room_height), (window_x + window_size, room_y + room_height))
                
            elif props["jendela"] == "selatan":  # sisi bawah
                window_x = room_x + room_width/3
                msp.add_line((window_x, room_y), (window_x + window_size, room_y))
            
            y_offset += room_height + 50

    doc.saveas(filename)
    print(f"✅ File DXF berhasil dibuat: {filename}")

def draw_svg(objects, filename="hasil.svg"):
    """Buat file SVG dari objek dengan skala otomatis."""
    SCALE = 0.5
    MARGIN = 20
    
    # Hitung ukuran total yang dibutuhkan
    total_height = 0
    max_width = 0
    
    for obj, props in objects.items():
        if obj == "kursi":
            total_height += max(props["lebar"], props["tinggi"]) + 50
            max_width = max(max_width, props["panjang"] * 2 + 50)
        elif obj == "ruangan":
            total_height += props["lebar"] + 50
            max_width = max(max_width, props["panjang"])
    
    dwg = svgwrite.Drawing(
        filename,
        size=((max_width * SCALE + 2 * MARGIN), (total_height * SCALE + 2 * MARGIN)),
        profile="tiny"
    )
    
    y_offset = MARGIN
    
    for obj, props in objects.items():
        if obj == "kursi":
            # Tampak atas
            dwg.add(dwg.rect(
                insert=(MARGIN, y_offset),
                size=(props["panjang"] * SCALE, props["lebar"] * SCALE),
                stroke="black", fill="none", stroke_width=2
            ))
            
            # Kaki kursi
            dwg.add(dwg.circle(
                center=(MARGIN + 5 * SCALE, y_offset + 5 * SCALE), 
                r=3, stroke="black", fill="none"
            ))
            dwg.add(dwg.circle(
                center=(MARGIN + (props["panjang"] - 5) * SCALE, y_offset + 5 * SCALE), 
                r=3, stroke="black", fill="none"
            ))
            dwg.add(dwg.circle(
                center=(MARGIN + 5 * SCALE, y_offset + (props["lebar"] - 5) * SCALE), 
                r=3, stroke="black", fill="none"
            ))
            dwg.add(dwg.circle(
                center=(MARGIN + (props["panjang"] - 5) * SCALE, y_offset + (props["lebar"] - 5) * SCALE), 
                r=3, stroke="black", fill="none"
            ))
            
            # Tampak depan
            dwg.add(dwg.rect(
                insert=(MARGIN + props["panjang"] * SCALE + 20, y_offset),
                size=(props["panjang"] * SCALE, props["tinggi"] * SCALE),
                stroke="black", fill="none", stroke_width=2
            ))
            
            y_offset += max(props["lebar"], props["tinggi"]) * SCALE + 20
            
        elif obj == "ruangan":
            dwg.add(dwg.rect(
                insert=(MARGIN, y_offset),
                size=(props["panjang"] * SCALE, props["lebar"] * SCALE),
                stroke="blue", fill="none", stroke_width=2
            ))
            
            # Pintu
            if props["pintu"]:
                door_color = "brown"
                if props["pintu"] == "barat":  # kiri
                    dwg.add(dwg.line(
                        start=(MARGIN, y_offset + props["lebar"]/2 * SCALE),
                        end=(MARGIN, y_offset + (props["lebar"]/2 + 20) * SCALE),
                        stroke=door_color, stroke_width=3
                    ))
                elif props["pintu"] == "timur":  # kanan
                    dwg.add(dwg.line(
                        start=(MARGIN + props["panjang"] * SCALE, y_offset + props["lebar"]/2 * SCALE),
                        end=(MARGIN + props["panjang"] * SCALE, y_offset + (props["lebar"]/2 + 20) * SCALE),
                        stroke=door_color, stroke_width=3
                    ))
                elif props["pintu"] == "utara":  # atas
                    dwg.add(dwg.line(
                        start=(MARGIN + props["panjang"]/2 * SCALE, y_offset + props["lebar"] * SCALE),
                        end=(MARGIN + (props["panjang"]/2 + 20) * SCALE, y_offset + props["lebar"] * SCALE),
                        stroke=door_color, stroke_width=3
                    ))
                elif props["pintu"] == "selatan":  # bawah
                    dwg.add(dwg.line(
                        start=(MARGIN + props["panjang"]/2 * SCALE, y_offset),
                        end=(MARGIN + (props["panjang"]/2 + 20) * SCALE, y_offset),
                        stroke=door_color, stroke_width=3
                    ))
            
            # Jendela
            if props["jendela"]:
                window_color = "green"
                if props["jendela"] == "barat":  # kiri
                    dwg.add(dwg.rect(
                        insert=(MARGIN - 5, y_offset + props["lebar"]/3 * SCALE),
                        size=(5, 15 * SCALE),
                        stroke=window_color, fill="lightblue", stroke_width=1
                    ))
                elif props["jendela"] == "timur":  # kanan
                    dwg.add(dwg.rect(
                        insert=(MARGIN + props["panjang"] * SCALE, y_offset + props["lebar"]/3 * SCALE),
                        size=(5, 15 * SCALE),
                        stroke=window_color, fill="lightblue", stroke_width=1
                    ))
                elif props["jendela"] == "utara":  # atas
                    dwg.add(dwg.rect(
                        insert=(MARGIN + props["panjang"]/3 * SCALE, y_offset + props["lebar"] * SCALE),
                        size=(15 * SCALE, 5),
                        stroke=window_color, fill="lightblue", stroke_width=1
                    ))
                elif props["jendela"] == "selatan":  # bawah
                    dwg.add(dwg.rect(
                        insert=(MARGIN + props["panjang"]/3 * SCALE, y_offset - 5),
                        size=(15 * SCALE, 5),
                        stroke=window_color, fill="lightblue", stroke_width=1
                    ))
            
            y_offset += props["lebar"] * SCALE + 20
    
    dwg.save()
    print(f"✅ File SVG berhasil dibuat: {filename}")

def run_tests():
    """Fungsi testing sederhana."""
    print("🚀 Menjalankan tests...")
    
    test_cases = [
        "Kursi dengan 4 kaki, dudukan persegi 40x40 cm, tinggi 45 cm",
        "Ruangan ukuran 4x5 meter, dengan 1 pintu di sisi barat dan 1 jendela di sisi utara",
        "Ruangan ukuran 3x3 meter dengan pintu di timur",
        "Kursi kayu 50x50 cm tinggi 60 cm"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_case}'")
        result = parse_description(test_case)
        if result:
            print(f"✅ Berhasil parsing: {result}")
            # Coba buat file untuk test
            draw_dxf(result, f"test_{i}.dxf")
            draw_svg(result, f"test_{i}.svg")
        else:
            print("❌ Gagal parsing")
    
    print("\n📊 Testing selesai!")

if __name__ == "__main__":
    # Jalankan tests otomatis
    run_tests()
    
    # Input manual (opsional)
    print("\n" + "="*50)
    deskripsi = input("Masukkan deskripsi (atau tekan Enter untuk menggunakan hasil test): ")
    
    if deskripsi.strip():
        objek = parse_description(deskripsi)
        if not objek:
            print("❌ Deskripsi tidak dikenali.")
        else:
            draw_dxf(objek, "hasil.dxf")
            draw_svg(objek, "hasil.svg")
    else:
        print("✅ Menggunakan file test yang sudah dibuat.")