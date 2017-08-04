#!/usr/bin/env python

from construct import *

Atari800_MACHINE_XLXE = 1
MEMORY_RAM_320_RAMBO = 320
MEMORY_RAM_320_COMPY_SHOP = 321
BB_RAM_SIZE = 0x10000
COMMAND_FRAME_SIZE = 6
DATA_BUFFER_SIZE = 256 + 3

def init_atari800_struct():
    Fname = Struct(
        "filelen" / Int16ul,
        "filename" / String(this.filelen),
        )

    Sio = Struct(
        "status" / Int32sl,
        "filename" / Fname,
        )

    a8save = "a8save" / Struct(
        "signature" / Const(b"ATARI800"),
        "version" / Int8ul,
        "verbose" / Int8ul,

        "tv_mode" / Int8ul,
        "machine_type" / Int8ul,

        "xl_xe" / If(this.machine_type > 0,
            Struct(
                "builtin_basic" / Int8ul,
                "keyboard_leds" / Int8ul,
                "f_keys" / Int8ul,
                "jumper" / Int8ul,
                "builtin_game" / Int8ul,
                "keyboard_detached" / Int8ul,
                )
            ),

        # CARTRIDGE
        "left_cart_type" / Int32sl,
        "left_cart_filename" / If(this.left_cart_type > 0, Fname),
        "left_cart_state" / If(this.left_cart_type > 0, Int32sl),

        "right_cart" / If(this.left_cart_type < 0,
            Struct(
                "type" / Int32sl,
                "filename" / Fname,
                "state" / Int32sl,
                )
            ),

        # SIO
        # StateSav_SaveINT((int *) &SIO_drive_status[i], 1);
        # StateSav_SaveFNAME(SIO_filename[i]);
        "sio_1" / Sio,
        "sio_2" / Sio,
        "sio_3" / Sio,
        "sio_4" / Sio,
        "sio_5" / Sio,
        "sio_6" / Sio,
        "sio_7" / Sio,
        "sio_8" / Sio,

        # ANTIC
        "antic" / Struct(
            "DMACTL" / Int8ul,
            "CHACTL" / Int8ul,
            "HSCROL" / Int8ul,
            "VSCROL" / Int8ul,
            "PMBASE" / Int8ul,
            "CHBASE" / Int8ul,
            "NMIEN" / Int8ul,
            "NMIST" / Int8ul,
            "IR" / Int8ul,
            "anticmode" / Int8ul,
            "dctr" / Int8ul,
            "lastline" / Int8ul,
            "need_dl" / Int8ul,
            "vscrol_off" / Int8ul,

            "dlist" / Int16ul,
            "screenaddr" / Int16ul,

            "xpos" / Int32sl,
            "xpos_limit" / Int32sl,
            "ypos" / Int32sl,
            ),

        #CPU
        "cpu" / Struct(
            "A" / Int8ul,
            "P" / Int8ul,
            "S" / Int8ul,
            "X" / Int8ul,
            "Y" / Int8ul,
            "IRQ" / Int8ul,
            ),

        #Memory
        "axlon" / If(this.machine_type == 0,
            Struct(
                "num_banks" / Int8ul,
                "curbank" / If (this.num_banks > 0, Int32sl),
                "0f_mirror" / If (this.num_banks > 0, Int32sl),
                "ram" / If (this.num_banks > 0, Bytes(this.num_banks * 0x4000)),
                )
            ),

        "mosaic" / If(this.machine_type == 0,
            Struct(
                "num_banks" / Int8ul,
                "curbank" / If (this.num_banks > 0, Int32sl),
                "ram" / If (this.num_banks > 0, Bytes(this.num_banks * 0x1000)),
                )
            ),

        "ram" / Struct(
            "base_ram_size_kb" / Int32sl,
            "ram" / Bytes(65536),
            "attrib" / Bytes(65536),
            ),

        "ram_xlxe" / If(this.machine_type == Atari800_MACHINE_XLXE,
            Struct(
                "basic" / If(this._.verbose != 0, Bytes(8192)),
                "under_cartA0BF" / Bytes(8192),
                "os" / If(this._.verbose != 0, Bytes(16384)),
                "under_atarixl_os" / Bytes(16384),
                "xegame" / If(this._.verbose != 0, Bytes(0x2000)),
                )
            ),

        "num_16k_xe_banks" / Int32sl,

        "ram_size_kb_before_rambo" / Computed(this.ram.base_ram_size_kb + (this.num_16k_xe_banks * 16)),

        # rambo_kb will be populated if RAMBO = 320 (0x140), COMPY_SHOP = 321 (0x141)
        "rambo_kb" / IfThenElse(this.ram_size_kb_before_rambo & 0xfffe == 0x140, Int32sl, Computed(0)), # value is MEMORY_ram_size - 320

        "ram_size" / Computed(this.ram_size_kb_before_rambo + this.rambo_kb),

        "portb" / Int8ul,

        "cartA0BF_enabled" / Int32sl,

        "atarixe_memory" / If(this.ram_size > 64,
            Struct(
                "size" / Computed((1 + (this.ram_size - 64) / 16) * 16384),
                "ram" / Bytes(this.size),
                "selftest_enabled" / Computed(lambda ctx: (ctx._.portb & 0x81) == 0x01 and not ((ctx._.portb & 0x30) != 0x30 and ctx._.ram_size == MEMORY_RAM_320_COMPY_SHOP) and not ((ctx._.portb & 0x10) == 0 and ctx._.ram_size == 1088)),
                "antic_bank_under_selftest" / If(this.selftest_enabled, Bytes(0x800)),
                )
            ),

        "mapram" / If(lambda ctx: ctx.machine_type == Atari800_MACHINE_XLXE and ctx.ram_size > 20,
            Struct(
                "enable" / Int32sl,
                "memory" / If(this.enable != 0, Bytes(0x800)),
                )
            ),

        "PC" / Int16ul,

        "gtia" / Struct(
            "HPOSP0" / Int8ul,
            "HPOSP1" / Int8ul,
            "HPOSP2" / Int8ul,
            "HPOSP3" / Int8ul,
            "HPOSM0" / Int8ul,
            "HPOSM1" / Int8ul,
            "HPOSM2" / Int8ul,
            "HPOSM3" / Int8ul,
            "PF0PM" / Int8ul,
            "PF1PM" / Int8ul,
            "PF2PM" / Int8ul,
            "PF3PM" / Int8ul,
            "M0PL" / Int8ul,
            "M1PL" / Int8ul,
            "M2PL" / Int8ul,
            "M3PL" / Int8ul,
            "P0PL" / Int8ul,
            "P1PL" / Int8ul,
            "P2PL" / Int8ul,
            "P3PL" / Int8ul,
            "SIZEP0" / Int8ul,
            "SIZEP1" / Int8ul,
            "SIZEP2" / Int8ul,
            "SIZEP3" / Int8ul,
            "SIZEM" / Int8ul,
            "GRAFP0" / Int8ul,
            "GRAFP1" / Int8ul,
            "GRAFP2" / Int8ul,
            "GRAFP3" / Int8ul,
            "GRAFM" / Int8ul,
            "COLPM0" / Int8ul,
            "COLPM1" / Int8ul,
            "COLPM2" / Int8ul,
            "COLPM3" / Int8ul,
            "COLPF0" / Int8ul,
            "COLPF1" / Int8ul,
            "COLPF2" / Int8ul,
            "COLPF3" / Int8ul,
            "COLBK" / Int8ul,
            "PRIOR" / Int8ul,
            "VDELAY" / Int8ul,
            "GRACTL" / Int8ul,

            "consol_mask" / Int8ul,
            "speaker" / Int32sl,
            "next_console_value" / Int32sl,
            "TRIG_latch" / Bytes(4),
            ),

        "pia" / Struct(
            "PACTL" / Int8ul,
            "PBCTL" / Int8ul,
            "PORTA" / Int8ul,
            "PORTB" / Int8ul,

            "PORTA_mask" / Int8ul,
            "PORTB_mask" / Int8ul,

            "CA2" / Int32sl,
            "CA2_negpending" / Int32sl,
            "CA2_pospending" / Int32sl,
            "CB2" / Int32sl,
            "CB2_negpending" / Int32sl,
            "CB2_pospending" / Int32sl,
            ),

        "pokey" / Struct(
            "KBCODE" / Int8ul,
            "IRQST" / Int8ul,
            "IRQEN" / Int8ul,
            "SKCTL" / Int8ul,

            "shift_key" / Int32sl,
            "keypressed" / Int32sl,
            "POKEY_DELAYED_SERIN_IRQ" / Int32sl,
            "POKEY_DELAYED_SEROUT_IRQ" / Int32sl,
            "POKEY_DELAYED_XMTDONE_IRQ" / Int32sl,

            "AUDF" / Bytes(4),
            "AUDC" / Bytes(4),
            "AUDCTL" / Int8ul,

            "DivNIRQ" / Bytes(16),
            "DivNMax" / Bytes(16),
            "Base_mult" / Int32sl,

            ),

        "xep80_enabled" / Int8ul,
        "xep80" / If(this.xep80_enabled,
            Struct(
                "tbd" / Bytes(8330),
                # 25 INT,1 => 100 bytes
                # 1 WORD,10 => 10 bytes
                # 3 BYTE, 1 => 3 bytes
                # 1 BYTE, 25 => 25 bytes
                # 8192 video ram
                # ---------
                # 8330 bytes
                #
                # INT(&XEP80_port, 1);
                # INT(&show_xep80, 1);
                # INT(&num_ticks, 1);
                # INT(&output_word, 1);
                # INT(&input_count, 1);
                # INT(&receiving, 1);
                # UWORD(input_queue, 10);
                # INT(&receiving, 1);
                # UBYTE(&last_char, 1);
                # INT(&xpos, 1);
                # INT(&xscroll, 1);
                # INT(&ypos, 1);
                # INT(&cursor_x, 1);
                # INT(&cursor_y, 1);
                # INT(&curs, 1);
                # INT(&old_xpos, 1);
                # INT(&old_ypos, 1);
                # INT(&lmargin, 1);
                # INT(&rmargin, 1);
                # UBYTE(&attrib_a, 1);
                # UBYTE(&attrib_b, 1);
                # INT(&list_mode, 1);
                # INT(&escape_mode, 1);
                # INT(&char_set, 1);
                # INT(&cursor_on, 1);
                # INT(&cursor_blink, 1);
                # INT(&cursor_overwrite, 1);
                # INT(&blink_reverse, 1);
                # INT(&inverse_mode, 1);
                # INT(&screen_output, 1);
                # INT(&burst_mode, 1);
                # INT(&graphics_mode, 1);
                # INT(&pal_mode, 1);
                # UBYTE(&ptr, 25);
                # UBYTE(video_ram, 8192);
                )
            ),

        "PBI" / Struct(
            "D1FF_LATCH" / Int8ul,
            "D6D7ram" / Int32sl,
            "IRQ" / Int32sl,
            ),

        "PBI" / Struct(
            "D1FF_LATCH" / Int8ul,
            "D6D7ram" / Int32sl,
            "IRQ" / Int32sl,
            ),

        "PBI_MIO_enabled" / Int8ul,
        "PBI_MIO" / If(this.PBI_MIO_enabled,
            Struct(
                "scsi_disk_filename" / Fname,
                "rom_filename" / Fname,
                "ram_size" / Int32sl,
                "ram_bank_offset" / Int32sl,
                "ram" / Bytes(this.ram_size),
                "rom_bank" / Int8ul,
                "ram_enabled" / Int32sl,
                )
            ),

        "PBI_BB_enabled" / Int8ul,
        "PBI_BB" / If(this.PBI_BB_enabled,
            Struct(
                "scsi_disk_filename" / Fname,
                "rom_filename" / Fname,
                "ram_bank_offset" / Int32sl,
                "ram" / Bytes(BB_RAM_SIZE),
                "rom_bank" / Int8ul,
                "rom_high_bit" / Int32sl,
                "pcr" / Int8ul,
                )
            ),

        "PBI_XLD_enabled" / Int8ul,
        "PBI_XLD" / If(this.PBI_XLD_enabled,
            Struct(
                "xld_v_enabled" / Int32sl,
                "xld_d_enabled" / Int32sl,
                "xld_d_romfilename" / Fname,
                "xld_v_romfilename" / Fname,
                "votrax_latch" / Int8ul,
                "modem_latch" / Int8ul,
                "CommandFrame" / Bytes(COMMAND_FRAME_SIZE),
                "CommandIndex" / Int32sl,
                "DataBuffer" / Bytes(DATA_BUFFER_SIZE),
                "DataIndex" / Int32sl,
                "TransferStatus" / Int32sl,
                "ExpectedBytes" / Int32sl,
                "VOTRAXSND_busy" / Int32sl,
              )
            ),

        )

    return a8save

if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rb") as fh:
        data = fh.read()
        a8save = init_atari800_struct()
        test = a8save.parse(data)
        print test
