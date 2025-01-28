-- Copyright (C) 2020  Intel Corporation. All rights reserved.
-- Your use of Intel Corporation's design tools, logic functions 
-- and other software and tools, and any partner logic 
-- functions, and any output files from any of the foregoing 
-- (including device programming or simulation files), and any 
-- associated documentation or information are expressly subject 
-- to the terms and conditions of the Intel Program License 
-- Subscription Agreement, the Intel Quartus Prime License Agreement,
-- the Intel FPGA IP License Agreement, or other applicable license
-- agreement, including, without limitation, that your use is for
-- the sole purpose of programming logic devices manufactured by
-- Intel and sold by Intel or its authorized distributors.  Please
-- refer to the applicable agreement for further details, at
-- https://fpgasoftware.intel.com/eula.

-- VENDOR "Altera"
-- PROGRAM "Quartus Prime"
-- VERSION "Version 20.1.0 Build 711 06/05/2020 SJ Lite Edition"

-- DATE "10/24/2022 15:48:57"

-- 
-- Device: Altera EP4CE6E22C6 Package TQFP144
-- 

-- 
-- This VHDL file should be used for ModelSim-Altera (VHDL) only
-- 

LIBRARY CYCLONEIVE;
LIBRARY IEEE;
USE CYCLONEIVE.CYCLONEIVE_COMPONENTS.ALL;
USE IEEE.STD_LOGIC_1164.ALL;

ENTITY 	hard_block IS
    PORT (
	devoe : IN std_logic;
	devclrn : IN std_logic;
	devpor : IN std_logic
	);
END hard_block;

-- Design Ports Information
-- ~ALTERA_ASDO_DATA1~	=>  Location: PIN_6,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- ~ALTERA_FLASH_nCE_nCSO~	=>  Location: PIN_8,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- ~ALTERA_DCLK~	=>  Location: PIN_12,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- ~ALTERA_DATA0~	=>  Location: PIN_13,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- ~ALTERA_nCEO~	=>  Location: PIN_101,	 I/O Standard: 2.5 V,	 Current Strength: 8mA


ARCHITECTURE structure OF hard_block IS
SIGNAL gnd : std_logic := '0';
SIGNAL vcc : std_logic := '1';
SIGNAL unknown : std_logic := 'X';
SIGNAL ww_devoe : std_logic;
SIGNAL ww_devclrn : std_logic;
SIGNAL ww_devpor : std_logic;
SIGNAL \~ALTERA_ASDO_DATA1~~padout\ : std_logic;
SIGNAL \~ALTERA_FLASH_nCE_nCSO~~padout\ : std_logic;
SIGNAL \~ALTERA_DATA0~~padout\ : std_logic;
SIGNAL \~ALTERA_ASDO_DATA1~~ibuf_o\ : std_logic;
SIGNAL \~ALTERA_FLASH_nCE_nCSO~~ibuf_o\ : std_logic;
SIGNAL \~ALTERA_DATA0~~ibuf_o\ : std_logic;

BEGIN

ww_devoe <= devoe;
ww_devclrn <= devclrn;
ww_devpor <= devpor;
END structure;


LIBRARY CYCLONEIVE;
LIBRARY IEEE;
USE CYCLONEIVE.CYCLONEIVE_COMPONENTS.ALL;
USE IEEE.STD_LOGIC_1164.ALL;

ENTITY 	flipFlopD IS
    PORT (
	clk : IN std_logic;
	D : IN std_logic;
	nSet : IN std_logic;
	nRst : IN std_logic;
	Q : OUT std_logic;
	nQ : OUT std_logic
	);
END flipFlopD;

-- Design Ports Information
-- Q	=>  Location: PIN_33,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- nQ	=>  Location: PIN_34,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- nRst	=>  Location: PIN_44,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- D	=>  Location: PIN_31,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- nSet	=>  Location: PIN_32,	 I/O Standard: 2.5 V,	 Current Strength: Default
-- clk	=>  Location: PIN_28,	 I/O Standard: 2.5 V,	 Current Strength: Default


ARCHITECTURE structure OF flipFlopD IS
SIGNAL gnd : std_logic := '0';
SIGNAL vcc : std_logic := '1';
SIGNAL unknown : std_logic := 'X';
SIGNAL devoe : std_logic := '1';
SIGNAL devclrn : std_logic := '1';
SIGNAL devpor : std_logic := '1';
SIGNAL ww_devoe : std_logic;
SIGNAL ww_devclrn : std_logic;
SIGNAL ww_devpor : std_logic;
SIGNAL ww_clk : std_logic;
SIGNAL ww_D : std_logic;
SIGNAL ww_nSet : std_logic;
SIGNAL ww_nRst : std_logic;
SIGNAL ww_Q : std_logic;
SIGNAL ww_nQ : std_logic;
SIGNAL \Q~output_o\ : std_logic;
SIGNAL \nQ~output_o\ : std_logic;
SIGNAL \nRst~input_o\ : std_logic;
SIGNAL \D~input_o\ : std_logic;
SIGNAL \nSet~input_o\ : std_logic;
SIGNAL \clk~input_o\ : std_logic;
SIGNAL \sr20|nand0|y~1_combout\ : std_logic;
SIGNAL \sr30|nand0|y~1_combout\ : std_logic;
SIGNAL \sr30|nand0|y~2_combout\ : std_logic;
SIGNAL \sr31|nand0|y~1_combout\ : std_logic;
SIGNAL \sr31|nand1|y~0_combout\ : std_logic;
SIGNAL \sr31|nand0|y~2_combout\ : std_logic;
SIGNAL \sr31|nand1|y~1_combout\ : std_logic;
SIGNAL \sr31|nand0|ALT_INV_y~2_combout\ : std_logic;
SIGNAL \sr31|nand1|ALT_INV_y~1_combout\ : std_logic;

COMPONENT hard_block
    PORT (
	devoe : IN std_logic;
	devclrn : IN std_logic;
	devpor : IN std_logic);
END COMPONENT;

BEGIN

ww_clk <= clk;
ww_D <= D;
ww_nSet <= nSet;
ww_nRst <= nRst;
Q <= ww_Q;
nQ <= ww_nQ;
ww_devoe <= devoe;
ww_devclrn <= devclrn;
ww_devpor <= devpor;
\sr31|nand0|ALT_INV_y~2_combout\ <= NOT \sr31|nand0|y~2_combout\;
\sr31|nand1|ALT_INV_y~1_combout\ <= NOT \sr31|nand1|y~1_combout\;
auto_generated_inst : hard_block
PORT MAP (
	devoe => ww_devoe,
	devclrn => ww_devclrn,
	devpor => ww_devpor);

-- Location: IOOBUF_X0_Y6_N23
\Q~output\ : cycloneive_io_obuf
-- pragma translate_off
GENERIC MAP (
	bus_hold => "false",
	open_drain_output => "false")
-- pragma translate_on
PORT MAP (
	i => \sr31|nand0|ALT_INV_y~2_combout\,
	devoe => ww_devoe,
	o => \Q~output_o\);

-- Location: IOOBUF_X0_Y5_N16
\nQ~output\ : cycloneive_io_obuf
-- pragma translate_off
GENERIC MAP (
	bus_hold => "false",
	open_drain_output => "false")
-- pragma translate_on
PORT MAP (
	i => \sr31|nand1|ALT_INV_y~1_combout\,
	devoe => ww_devoe,
	o => \nQ~output_o\);

-- Location: IOIBUF_X5_Y0_N15
\nRst~input\ : cycloneive_io_ibuf
-- pragma translate_off
GENERIC MAP (
	bus_hold => "false",
	simulate_z_as => "z")
-- pragma translate_on
PORT MAP (
	i => ww_nRst,
	o => \nRst~input_o\);

-- Location: IOIBUF_X0_Y7_N1
\D~input\ : cycloneive_io_ibuf
-- pragma translate_off
GENERIC MAP (
	bus_hold => "false",
	simulate_z_as => "z")
-- pragma translate_on
PORT MAP (
	i => ww_D,
	o => \D~input_o\);

-- Location: IOIBUF_X0_Y6_N15
\nSet~input\ : cycloneive_io_ibuf
-- pragma translate_off
GENERIC MAP (
	bus_hold => "false",
	simulate_z_as => "z")
-- pragma translate_on
PORT MAP (
	i => ww_nSet,
	o => \nSet~input_o\);

-- Location: IOIBUF_X0_Y9_N8
\clk~input\ : cycloneive_io_ibuf
-- pragma translate_off
GENERIC MAP (
	bus_hold => "false",
	simulate_z_as => "z")
-- pragma translate_on
PORT MAP (
	i => ww_clk,
	o => \clk~input_o\);

-- Location: LCCOMB_X5_Y6_N28
\sr20|nand0|y~1\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr20|nand0|y~1_combout\ = (\clk~input_o\ & !\sr30|nand0|y~1_combout\)

-- pragma translate_off
GENERIC MAP (
	lut_mask => "0000000010101010",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	dataa => \clk~input_o\,
	datad => \sr30|nand0|y~1_combout\,
	combout => \sr20|nand0|y~1_combout\);

-- Location: LCCOMB_X5_Y6_N24
\sr30|nand0|y~1\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr30|nand0|y~1_combout\ = (\nRst~input_o\ & (!\sr20|nand0|y~1_combout\ & (\nSet~input_o\ & \sr30|nand0|y~2_combout\)))

-- pragma translate_off
GENERIC MAP (
	lut_mask => "0010000000000000",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	dataa => \nRst~input_o\,
	datab => \sr20|nand0|y~1_combout\,
	datac => \nSet~input_o\,
	datad => \sr30|nand0|y~2_combout\,
	combout => \sr30|nand0|y~1_combout\);

-- Location: LCCOMB_X5_Y6_N10
\sr30|nand0|y~2\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr30|nand0|y~2_combout\ = (!\sr30|nand0|y~1_combout\) # (!\clk~input_o\)

-- pragma translate_off
GENERIC MAP (
	lut_mask => "0101010111111111",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	dataa => \clk~input_o\,
	datad => \sr30|nand0|y~1_combout\,
	combout => \sr30|nand0|y~2_combout\);

-- Location: LCCOMB_X5_Y6_N12
\sr31|nand0|y~1\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr31|nand0|y~1_combout\ = (\nSet~input_o\ & (((\sr30|nand0|y~2_combout\) # (!\D~input_o\)) # (!\nRst~input_o\)))

-- pragma translate_off
GENERIC MAP (
	lut_mask => "1111000001110000",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	dataa => \nRst~input_o\,
	datab => \D~input_o\,
	datac => \nSet~input_o\,
	datad => \sr30|nand0|y~2_combout\,
	combout => \sr31|nand0|y~1_combout\);

-- Location: LCCOMB_X5_Y6_N0
\sr31|nand1|y~0\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr31|nand1|y~0_combout\ = (\nRst~input_o\ & ((\D~input_o\) # ((\sr30|nand0|y~2_combout\) # (!\nSet~input_o\))))

-- pragma translate_off
GENERIC MAP (
	lut_mask => "1010101010001010",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	dataa => \nRst~input_o\,
	datab => \D~input_o\,
	datac => \nSet~input_o\,
	datad => \sr30|nand0|y~2_combout\,
	combout => \sr31|nand1|y~0_combout\);

-- Location: LCCOMB_X5_Y6_N14
\sr31|nand0|y~2\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr31|nand0|y~2_combout\ = (\sr31|nand0|y~1_combout\ & ((\sr31|nand0|y~2_combout\) # (!\sr31|nand1|y~0_combout\)))

-- pragma translate_off
GENERIC MAP (
	lut_mask => "1010001010100010",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	dataa => \sr31|nand0|y~1_combout\,
	datab => \sr31|nand1|y~0_combout\,
	datac => \sr31|nand0|y~2_combout\,
	combout => \sr31|nand0|y~2_combout\);

-- Location: LCCOMB_X5_Y6_N26
\sr31|nand1|y~1\ : cycloneive_lcell_comb
-- Equation(s):
-- \sr31|nand1|y~1_combout\ = (\sr31|nand1|y~0_combout\ & !\sr31|nand0|y~2_combout\)

-- pragma translate_off
GENERIC MAP (
	lut_mask => "0000110000001100",
	sum_lutc_input => "datac")
-- pragma translate_on
PORT MAP (
	datab => \sr31|nand1|y~0_combout\,
	datac => \sr31|nand0|y~2_combout\,
	combout => \sr31|nand1|y~1_combout\);

ww_Q <= \Q~output_o\;

ww_nQ <= \nQ~output_o\;
END structure;


