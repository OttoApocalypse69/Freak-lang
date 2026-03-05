#include "freak_runtime.h"
#include <string.h>

/* --- Global variables --- */
freak_word output = { 0 };
freak_word src = { 0 };
int64_t pos = 0;
int64_t cur_line = 0;
int64_t indent_level = 0;
freak_word var_registry = { 0 };
freak_word fwd_decls = { 0 };
freak_word input_file = { 0 };
freak_word source = { 0 };
int64_t src_len = 0;
freak_word c_result = { 0 };
freak_word output_c = { 0 };

/* --- Forward declarations --- */
static void freak_emit(freak_word s);
static void freak_emit_line(freak_word s);
static bool freak_is_digit(freak_word ch);
static bool freak_is_alpha(freak_word ch);
static bool freak_is_alnum(freak_word ch);
static bool freak_at_end(void);
static freak_word freak_cur_ch(void);
static freak_word freak_ch_at(int64_t offset);
static freak_word freak_advance(void);
static void freak_skip_ws(void);
static void freak_skip_inline(void);
static bool freak_match_kw(freak_word kw);
static void freak_eat_kw(freak_word kw);
static freak_word freak_scan_ident(void);
static freak_word freak_scan_number(void);
static freak_word freak_scan_string(void);
static freak_word freak_c_escape(freak_word s);
static freak_word freak_ind(void);
static void freak_var_set(freak_word name, freak_word vtype);
static freak_word freak_var_get_type(freak_word name);
static freak_word freak_build_interpolation(freak_word s);
static freak_word freak_compile_primary(void);
static freak_word freak_compile_args(void);
static freak_word freak_compile_postfix(void);
static freak_word freak_compile_unary(void);
static freak_word freak_compile_mul(void);
static freak_word freak_compile_add(void);
static freak_word freak_compile_cmp(void);
static freak_word freak_compile_logic(void);
static freak_word freak_compile_expr(void);
static void freak_compile_block(void);
static void freak_compile_stmt(void);
static freak_word freak_compile_program(freak_word source);

/* --- Function definitions --- */
static void freak_emit(freak_word s) {
    output = freak_word_concat(output, s);
}

static void freak_emit_line(freak_word s) {
    output = freak_word_concat(freak_word_concat(output, s), freak_word_lit("\n"));
}

static bool freak_is_digit(freak_word ch) {
    if (freak_word_eq(ch, freak_word_lit("0"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("1"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("2"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("3"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("4"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("5"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("6"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("7"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("8"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("9"))) {
        return true;
    }
    return false;
}

static bool freak_is_alpha(freak_word ch) {
    if (freak_word_eq(ch, freak_word_lit("_"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("a"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("b"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("c"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("d"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("e"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("f"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("g"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("h"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("i"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("j"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("k"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("l"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("m"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("n"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("o"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("p"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("q"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("r"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("s"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("t"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("u"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("v"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("w"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("x"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("y"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("z"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("A"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("B"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("C"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("D"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("E"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("F"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("G"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("H"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("I"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("J"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("K"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("L"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("M"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("N"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("O"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("P"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("Q"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("R"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("S"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("T"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("U"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("V"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("W"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("X"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("Y"))) {
        return true;
    }
    if (freak_word_eq(ch, freak_word_lit("Z"))) {
        return true;
    }
    return false;
}

static bool freak_is_alnum(freak_word ch) {
    if (freak_is_alpha(ch)) {
        return true;
    }
    if (freak_is_digit(ch)) {
        return true;
    }
    return false;
}

static bool freak_at_end(void) {
    return (pos >= freak_word_length(src));
}

static freak_word freak_cur_ch(void) {
    if (freak_at_end()) {
        return freak_word_lit("");
    }
    return freak_word_char_at(src, pos);
}

static freak_word freak_ch_at(int64_t offset) {
    if (((pos + offset) >= freak_word_length(src))) {
        return freak_word_lit("");
    }
    return freak_word_char_at(src, (pos + offset));
}

static freak_word freak_advance(void) {
    freak_word c = freak_word_char_at(src, pos);
    pos += ((int64_t)1);
    if (freak_word_eq(c, freak_word_lit("\n"))) {
        cur_line += ((int64_t)1);
    }
    return c;
}

static void freak_skip_ws(void) {
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit(" "))) {
            pos += ((int64_t)1);
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("\t"))) {
            pos += ((int64_t)1);
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("\r"))) {
            pos += ((int64_t)1);
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("\n"))) {
            pos += ((int64_t)1);
            cur_line += ((int64_t)1);
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("-"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("-"))) {
                bool eol = false;
                while (!(eol)) {
                    if (freak_at_end()) {
                        eol = true;
                    } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("\n"))) {
                        eol = true;
                    } else {
                        pos += ((int64_t)1);
                    }
                }
            } else {
                fin = true;
            }
        } else {
            fin = true;
        }
    }
}

static void freak_skip_inline(void) {
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit(" "))) {
            pos += ((int64_t)1);
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("\t"))) {
            pos += ((int64_t)1);
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("\r"))) {
            pos += ((int64_t)1);
        } else {
            fin = true;
        }
    }
}

static bool freak_match_kw(freak_word kw) {
    int64_t kwlen = freak_word_length(kw);
    if (((pos + kwlen) > freak_word_length(src))) {
        return false;
    }
    int64_t i = ((int64_t)0);
    bool is_match = true;
    for (int64_t __rep_1 = 0; __rep_1 < kwlen; __rep_1++) {
        if (is_match) {
            if ((!freak_word_eq(freak_word_char_at(src, (pos + i)), freak_word_char_at(kw, i)))) {
                is_match = false;
            }
        }
        i += ((int64_t)1);
    }
    if ((!is_match)) {
        return false;
    }
    if (((pos + kwlen) < freak_word_length(src))) {
        freak_word nc = freak_word_char_at(src, (pos + kwlen));
        if (freak_is_alnum(nc)) {
            return false;
        }
    }
    return true;
}

static void freak_eat_kw(freak_word kw) {
    pos += freak_word_length(kw);
}

static freak_word freak_scan_ident(void) {
    freak_word res = freak_word_lit("");
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else {
            freak_word c = freak_cur_ch();
            if (freak_is_alnum(c)) {
                res = freak_word_concat(res, c);
                pos += ((int64_t)1);
            } else {
                fin = true;
            }
        }
    }
    return res;
}

static freak_word freak_scan_number(void) {
    freak_word res = freak_word_lit("");
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else {
            freak_word c = freak_cur_ch();
            if (freak_is_digit(c)) {
                res = freak_word_concat(res, c);
                pos += ((int64_t)1);
            } else if (freak_word_eq(c, freak_word_lit("."))) {
                res = freak_word_concat(res, c);
                pos += ((int64_t)1);
            } else {
                fin = true;
            }
        }
    }
    return res;
}

static freak_word freak_scan_string(void) {
    freak_word res = freak_word_lit("");
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else {
            freak_word c = freak_advance();
            if (freak_word_eq(c, freak_word_lit("\""))) {
                fin = true;
            } else if (freak_word_eq(c, freak_word_lit("\\"))) {
                freak_word esc = freak_advance();
                if (freak_word_eq(esc, freak_word_lit("n"))) {
                    res = freak_word_concat(res, freak_word_lit("\n"));
                } else if (freak_word_eq(esc, freak_word_lit("t"))) {
                    res = freak_word_concat(res, freak_word_lit("\t"));
                } else if (freak_word_eq(esc, freak_word_lit("\""))) {
                    res = freak_word_concat(res, freak_word_lit("\""));
                } else if (freak_word_eq(esc, freak_word_lit("\\"))) {
                    res = freak_word_concat(res, freak_word_lit("\\"));
                } else {
                    res = freak_word_concat(res, esc);
                }
            } else {
                res = freak_word_concat(res, c);
            }
        }
    }
    return res;
}

static freak_word freak_c_escape(freak_word s) {
    freak_word res = freak_word_lit("");
    int64_t i = ((int64_t)0);
    int64_t slen = freak_word_length(s);
    for (int64_t __rep_2 = 0; __rep_2 < slen; __rep_2++) {
        freak_word c = freak_word_char_at(s, i);
        if (freak_word_eq(c, freak_word_lit("\""))) {
            res = freak_word_concat(res, freak_word_lit("\\\""));
        } else if (freak_word_eq(c, freak_word_lit("\\"))) {
            res = freak_word_concat(res, freak_word_lit("\\\\"));
        } else if (freak_word_eq(c, freak_word_lit("\n"))) {
            res = freak_word_concat(res, freak_word_lit("\\n"));
        } else if (freak_word_eq(c, freak_word_lit("\t"))) {
            res = freak_word_concat(res, freak_word_lit("\\t"));
        } else {
            res = freak_word_concat(res, c);
        }
        i += ((int64_t)1);
    }
    return res;
}

static freak_word freak_ind(void) {
    freak_word res = freak_word_lit("");
    int64_t i = ((int64_t)0);
    for (int64_t __rep_3 = 0; __rep_3 < indent_level; __rep_3++) {
        res = freak_word_concat(res, freak_word_lit("    "));
        i += ((int64_t)1);
    }
    return res;
}

static void freak_var_set(freak_word name, freak_word vtype) {
    var_registry = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(var_registry, name), freak_word_lit(":")), vtype), freak_word_lit(";"));
}

static freak_word freak_var_get_type(freak_word name) {
    freak_word search = freak_word_concat(name, freak_word_lit(":"));
    int64_t slen = freak_word_length(search);
    int64_t rlen = freak_word_length(var_registry);
    int64_t i = ((int64_t)0);
    bool found = false;
    freak_word res = freak_word_lit("i");
    for (int64_t __rep_4 = 0; __rep_4 < rlen; __rep_4++) {
        if ((!found)) {
            if (((i + slen) <= rlen)) {
                bool is_match = true;
                int64_t j = ((int64_t)0);
                for (int64_t __rep_5 = 0; __rep_5 < slen; __rep_5++) {
                    if (is_match) {
                        if ((!freak_word_eq(freak_word_char_at(var_registry, (i + j)), freak_word_char_at(search, j)))) {
                            is_match = false;
                        }
                    }
                    j += ((int64_t)1);
                }
                if (is_match) {
                    res = freak_word_char_at(var_registry, (i + slen));
                    found = true;
                }
            }
        }
        i += ((int64_t)1);
    }
    return res;
}

static freak_word freak_build_interpolation(freak_word s) {
    freak_word fmt = freak_word_lit("");
    freak_word args = freak_word_lit("");
    int64_t i = ((int64_t)0);
    int64_t slen = freak_word_length(s);
    bool fin = false;
    while (!(fin)) {
        if ((i >= slen)) {
            fin = true;
        } else {
            freak_word c = freak_word_char_at(s, i);
            if (freak_word_eq(c, freak_word_lit("{"))) {
                i += ((int64_t)1);
                freak_word vname = freak_word_lit("");
                bool inner_fin = false;
                while (!(inner_fin)) {
                    if ((i >= slen)) {
                        inner_fin = true;
                    } else {
                        freak_word vc = freak_word_char_at(s, i);
                        if (freak_word_eq(vc, freak_word_lit("}"))) {
                            i += ((int64_t)1);
                            inner_fin = true;
                        } else {
                            vname = freak_word_concat(vname, vc);
                            i += ((int64_t)1);
                        }
                    }
                }
                freak_word vtype = freak_var_get_type(vname);
                if ((!freak_word_eq(args, freak_word_lit("")))) {
                    args = freak_word_concat(args, freak_word_lit(", "));
                }
                if (freak_word_eq(vtype, freak_word_lit("w"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("%s"));
                    args = freak_word_concat(freak_word_concat(freak_word_concat(args, freak_word_lit("freak_word_to_cstr(freak_")), vname), freak_word_lit(")"));
                } else if (freak_word_eq(vtype, freak_word_lit("d"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("%g"));
                    args = freak_word_concat(freak_word_concat(args, freak_word_lit("freak_")), vname);
                } else if (freak_word_eq(vtype, freak_word_lit("b"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("%s"));
                    args = freak_word_concat(freak_word_concat(freak_word_concat(args, freak_word_lit("(freak_")), vname), freak_word_lit(" ? \"true\" : \"false\")"));
                } else {
                    fmt = freak_word_concat(fmt, freak_word_lit("%lld"));
                    args = freak_word_concat(freak_word_concat(args, freak_word_lit("(long long)freak_")), vname);
                }
            } else {
                if (freak_word_eq(c, freak_word_lit("\""))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("\\\""));
                } else if (freak_word_eq(c, freak_word_lit("\\"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("\\\\"));
                } else if (freak_word_eq(c, freak_word_lit("\n"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("\\n"));
                } else if (freak_word_eq(c, freak_word_lit("\t"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("\\t"));
                } else if (freak_word_eq(c, freak_word_lit("%"))) {
                    fmt = freak_word_concat(fmt, freak_word_lit("%%"));
                } else {
                    fmt = freak_word_concat(fmt, c);
                }
                i += ((int64_t)1);
            }
        }
    }
    if ((!freak_word_eq(args, freak_word_lit("")))) {
        return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_interpolate(\""), fmt), freak_word_lit("\", ")), args), freak_word_lit(")"));
    }
    return freak_word_concat(freak_word_concat(freak_word_lit("freak_word_lit(\""), fmt), freak_word_lit("\")"));
}

static freak_word freak_compile_primary(void) {
    freak_skip_inline();
    if (freak_at_end()) {
        return freak_word_lit("0");
    }
    freak_word c = freak_cur_ch();
    if (freak_is_digit(c)) {
        freak_word num = freak_scan_number();
        if (freak_word_contains(num, freak_word_lit("."))) {
            return num;
        }
        return freak_word_concat(freak_word_concat(freak_word_lit("((int64_t)"), num), freak_word_lit(")"));
    }
    if (freak_word_eq(c, freak_word_lit("\""))) {
        pos += ((int64_t)1);
        freak_word str_val = freak_scan_string();
        if (freak_word_contains(str_val, freak_word_lit("{"))) {
            return freak_build_interpolation(str_val);
        }
        return freak_word_concat(freak_word_concat(freak_word_lit("freak_word_lit(\""), freak_c_escape(str_val)), freak_word_lit("\")"));
    }
    if (freak_match_kw(freak_word_lit("true"))) {
        freak_eat_kw(freak_word_lit("true"));
        return freak_word_lit("true");
    }
    if (freak_match_kw(freak_word_lit("false"))) {
        freak_eat_kw(freak_word_lit("false"));
        return freak_word_lit("false");
    }
    if (freak_word_eq(c, freak_word_lit("("))) {
        pos += ((int64_t)1);
        freak_word inner = freak_compile_expr();
        freak_skip_inline();
        if (freak_word_eq(freak_cur_ch(), freak_word_lit(")"))) {
            pos += ((int64_t)1);
        }
        return freak_word_concat(freak_word_concat(freak_word_lit("("), inner), freak_word_lit(")"));
    }
    if (freak_is_alpha(c)) {
        freak_word name = freak_scan_ident();
        freak_skip_inline();
        if (freak_word_eq(freak_cur_ch(), freak_word_lit(":"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit(":"))) {
                pos += ((int64_t)2);
                freak_word sub = freak_scan_ident();
                freak_word fq = freak_word_concat(freak_word_concat(name, freak_word_lit("::")), sub);
                freak_skip_inline();
                if (freak_word_eq(freak_cur_ch(), freak_word_lit("("))) {
                    pos += ((int64_t)1);
                    freak_word cargs = freak_compile_args();
                    if (freak_word_eq(fq, freak_word_lit("fs::read"))) {
                        return freak_word_concat(freak_word_concat(freak_word_lit("freak_fs_read("), cargs), freak_word_lit(")"));
                    }
                    if (freak_word_eq(fq, freak_word_lit("fs::write"))) {
                        return freak_word_concat(freak_word_concat(freak_word_lit("freak_fs_write("), cargs), freak_word_lit(")"));
                    }
                    if (freak_word_eq(fq, freak_word_lit("process::args"))) {
                        return freak_word_concat(freak_word_concat(freak_word_lit("freak_process_args("), cargs), freak_word_lit(")"));
                    }
                    if (freak_word_eq(fq, freak_word_lit("process::exit"))) {
                        return freak_word_concat(freak_word_concat(freak_word_lit("freak_process_exit("), cargs), freak_word_lit(")"));
                    }
                    return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(name, freak_word_lit("_")), sub), freak_word_lit("(")), cargs), freak_word_lit(")"));
                }
                return freak_word_concat(freak_word_concat(name, freak_word_lit("_")), sub);
            }
        }
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("("))) {
            pos += ((int64_t)1);
            freak_word cargs = freak_compile_args();
            if (freak_word_eq(name, freak_word_lit("panic"))) {
                return freak_word_concat(freak_word_concat(freak_word_lit("freak_panic("), cargs), freak_word_lit(")"));
            }
            if (freak_word_eq(name, freak_word_lit("ask"))) {
                return freak_word_concat(freak_word_concat(freak_word_lit("freak_ask("), cargs), freak_word_lit(")"));
            }
            return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_"), name), freak_word_lit("(")), cargs), freak_word_lit(")"));
        }
        return freak_word_concat(freak_word_lit("freak_"), name);
    }
    pos += ((int64_t)1);
    return freak_word_lit("0");
}

static freak_word freak_compile_args(void) {
    freak_word res = freak_word_lit("");
    freak_skip_inline();
    if (freak_word_eq(freak_cur_ch(), freak_word_lit(")"))) {
        pos += ((int64_t)1);
        return res;
    }
    res = freak_compile_expr();
    freak_skip_inline();
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit(","))) {
            pos += ((int64_t)1);
            freak_skip_inline();
            res = freak_word_concat(freak_word_concat(res, freak_word_lit(", ")), freak_compile_expr());
            freak_skip_inline();
        } else {
            fin = true;
        }
    }
    if (freak_word_eq(freak_cur_ch(), freak_word_lit(")"))) {
        pos += ((int64_t)1);
    }
    return res;
}

static freak_word freak_compile_postfix(void) {
    freak_word res = freak_compile_primary();
    freak_skip_inline();
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("."))) {
            pos += ((int64_t)1);
            freak_word method = freak_scan_ident();
            freak_skip_inline();
            if (freak_word_eq(freak_cur_ch(), freak_word_lit("("))) {
                pos += ((int64_t)1);
                freak_word margs = freak_compile_args();
                if (freak_word_eq(method, freak_word_lit("length"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_lit("freak_word_length("), res), freak_word_lit(")"));
                } else if (freak_word_eq(method, freak_word_lit("char_at"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_word_char_at("), res), freak_word_lit(", ")), margs), freak_word_lit(")"));
                } else if (freak_word_eq(method, freak_word_lit("contains"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_word_contains("), res), freak_word_lit(", ")), margs), freak_word_lit(")"));
                } else if (freak_word_eq(method, freak_word_lit("starts_with"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_word_starts_with("), res), freak_word_lit(", ")), margs), freak_word_lit(")"));
                } else if (freak_word_eq(method, freak_word_lit("ends_with"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_word_ends_with("), res), freak_word_lit(", ")), margs), freak_word_lit(")"));
                } else if (freak_word_eq(method, freak_word_lit("trim"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_lit("freak_word_trim("), res), freak_word_lit(")"));
                } else if (freak_word_eq(method, freak_word_lit("to_int"))) {
                    res = freak_word_concat(freak_word_concat(freak_word_lit("freak_word_to_int("), res), freak_word_lit(")"));
                } else {
                    if ((!freak_word_eq(margs, freak_word_lit("")))) {
                        res = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_word_"), method), freak_word_lit("(")), res), freak_word_lit(", ")), margs), freak_word_lit(")"));
                    } else {
                        res = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_word_"), method), freak_word_lit("(")), res), freak_word_lit(")"));
                    }
                }
            } else {
                res = freak_word_concat(freak_word_concat(res, freak_word_lit(".")), method);
            }
            freak_skip_inline();
        } else {
            fin = true;
        }
    }
    return res;
}

static freak_word freak_compile_unary(void) {
    freak_skip_inline();
    if (freak_match_kw(freak_word_lit("not"))) {
        freak_eat_kw(freak_word_lit("not"));
        freak_word op = freak_compile_unary();
        return freak_word_concat(freak_word_concat(freak_word_lit("(!"), op), freak_word_lit(")"));
    }
    return freak_compile_postfix();
}

static freak_word freak_compile_mul(void) {
    freak_word left = freak_compile_unary();
    freak_skip_inline();
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("*"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("*"))) {
                pos += ((int64_t)2);
                freak_skip_inline();
                freak_word r = freak_compile_unary();
                left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("freak_pow_int("), left), freak_word_lit(", ")), r), freak_word_lit(")"));
                freak_skip_inline();
            } else if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                fin = true;
            } else {
                pos += ((int64_t)1);
                freak_skip_inline();
                freak_word r = freak_compile_unary();
                left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" * ")), r), freak_word_lit(")"));
                freak_skip_inline();
            }
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("/"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                fin = true;
            } else {
                pos += ((int64_t)1);
                freak_skip_inline();
                freak_word r = freak_compile_unary();
                left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" / ")), r), freak_word_lit(")"));
                freak_skip_inline();
            }
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("%"))) {
            pos += ((int64_t)1);
            freak_skip_inline();
            freak_word r = freak_compile_unary();
            left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" % ")), r), freak_word_lit(")"));
            freak_skip_inline();
        } else {
            fin = true;
        }
    }
    return left;
}

static freak_word freak_compile_add(void) {
    freak_word left = freak_compile_mul();
    freak_skip_inline();
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("+"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                fin = true;
            } else {
                pos += ((int64_t)1);
                freak_skip_inline();
                freak_word r = freak_compile_mul();
                left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" + ")), r), freak_word_lit(")"));
                freak_skip_inline();
            }
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("-"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                fin = true;
            } else if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit(">"))) {
                fin = true;
            } else {
                pos += ((int64_t)1);
                freak_skip_inline();
                freak_word r = freak_compile_mul();
                left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" - ")), r), freak_word_lit(")"));
                freak_skip_inline();
            }
        } else {
            fin = true;
        }
    }
    return left;
}

static freak_word freak_compile_cmp(void) {
    freak_word left = freak_compile_add();
    freak_skip_inline();
    if (freak_at_end()) {
        return left;
    }
    if (freak_word_eq(freak_cur_ch(), freak_word_lit("="))) {
        if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
            pos += ((int64_t)2);
            freak_skip_inline();
            freak_word r = freak_compile_add();
            return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" == ")), r), freak_word_lit(")"));
        }
    }
    if (freak_word_eq(freak_cur_ch(), freak_word_lit("!"))) {
        if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
            pos += ((int64_t)2);
            freak_skip_inline();
            freak_word r = freak_compile_add();
            return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" != ")), r), freak_word_lit(")"));
        }
    }
    if (freak_word_eq(freak_cur_ch(), freak_word_lit("<"))) {
        if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
            pos += ((int64_t)2);
            freak_skip_inline();
            freak_word r = freak_compile_add();
            return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" <= ")), r), freak_word_lit(")"));
        }
        pos += ((int64_t)1);
        freak_skip_inline();
        freak_word r = freak_compile_add();
        return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" < ")), r), freak_word_lit(")"));
    }
    if (freak_word_eq(freak_cur_ch(), freak_word_lit(">"))) {
        if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
            pos += ((int64_t)2);
            freak_skip_inline();
            freak_word r = freak_compile_add();
            return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" >= ")), r), freak_word_lit(")"));
        }
        pos += ((int64_t)1);
        freak_skip_inline();
        freak_word r = freak_compile_add();
        return freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" > ")), r), freak_word_lit(")"));
    }
    return left;
}

static freak_word freak_compile_logic(void) {
    freak_word left = freak_compile_cmp();
    freak_skip_inline();
    bool fin = false;
    while (!(fin)) {
        if (freak_at_end()) {
            fin = true;
        } else if (freak_match_kw(freak_word_lit("and"))) {
            freak_eat_kw(freak_word_lit("and"));
            freak_skip_inline();
            freak_word r = freak_compile_cmp();
            left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" && ")), r), freak_word_lit(")"));
            freak_skip_inline();
        } else if (freak_match_kw(freak_word_lit("or"))) {
            freak_eat_kw(freak_word_lit("or"));
            freak_skip_inline();
            freak_word r = freak_compile_cmp();
            left = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_lit("("), left), freak_word_lit(" || ")), r), freak_word_lit(")"));
            freak_skip_inline();
        } else {
            fin = true;
        }
    }
    return left;
}

static freak_word freak_compile_expr(void) {
    return freak_compile_logic();
}

static void freak_compile_block(void) {
    freak_skip_ws();
    if (freak_word_eq(freak_cur_ch(), freak_word_lit("{"))) {
        pos += ((int64_t)1);
    }
    freak_skip_ws();
    indent_level += ((int64_t)1);
    bool fin = false;
    while (!(fin)) {
        freak_skip_ws();
        if (freak_at_end()) {
            fin = true;
        } else if (freak_word_eq(freak_cur_ch(), freak_word_lit("}"))) {
            pos += ((int64_t)1);
            fin = true;
        } else {
            freak_compile_stmt();
        }
    }
    indent_level -= ((int64_t)1);
}

static void freak_compile_stmt(void) {
    freak_skip_ws();
    if (freak_at_end()) {
        return;
    }
    if (freak_match_kw(freak_word_lit("pilot"))) {
        freak_eat_kw(freak_word_lit("pilot"));
        freak_skip_inline();
        freak_word name = freak_scan_ident();
        freak_skip_inline();
        freak_word type_ann = freak_word_lit("");
        if (freak_word_eq(freak_cur_ch(), freak_word_lit(":"))) {
            pos += ((int64_t)1);
            freak_skip_inline();
            type_ann = freak_scan_ident();
            freak_skip_inline();
        }
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("="))) {
            pos += ((int64_t)1);
            freak_skip_inline();
            freak_word val = freak_compile_expr();
            freak_word ctype = freak_word_lit("int64_t");
            freak_word vtype = freak_word_lit("i");
            if (freak_word_eq(type_ann, freak_word_lit("word"))) {
                ctype = freak_word_lit("freak_word");
                vtype = freak_word_lit("w");
            } else if (freak_word_eq(type_ann, freak_word_lit("num"))) {
                ctype = freak_word_lit("double");
                vtype = freak_word_lit("d");
            } else if (freak_word_eq(type_ann, freak_word_lit("bool"))) {
                ctype = freak_word_lit("bool");
                vtype = freak_word_lit("b");
            } else if (freak_word_eq(type_ann, freak_word_lit("int"))) {
                ctype = freak_word_lit("int64_t");
                vtype = freak_word_lit("i");
            } else if ((!freak_word_eq(type_ann, freak_word_lit("")))) {
                ctype = type_ann;
                vtype = freak_word_lit("i");
            } else {
                if (freak_word_starts_with(val, freak_word_lit("freak_word_lit("))) {
                    ctype = freak_word_lit("freak_word");
                    vtype = freak_word_lit("w");
                } else if (freak_word_starts_with(val, freak_word_lit("freak_interpolate("))) {
                    ctype = freak_word_lit("freak_word");
                    vtype = freak_word_lit("w");
                } else if (freak_word_starts_with(val, freak_word_lit("freak_fs_read("))) {
                    ctype = freak_word_lit("freak_word");
                    vtype = freak_word_lit("w");
                } else if (freak_word_starts_with(val, freak_word_lit("freak_ask("))) {
                    ctype = freak_word_lit("freak_word");
                    vtype = freak_word_lit("w");
                } else if (freak_word_starts_with(val, freak_word_lit("freak_word_"))) {
                    ctype = freak_word_lit("freak_word");
                    vtype = freak_word_lit("w");
                } else if (freak_word_eq(val, freak_word_lit("true"))) {
                    ctype = freak_word_lit("bool");
                    vtype = freak_word_lit("b");
                } else if (freak_word_eq(val, freak_word_lit("false"))) {
                    ctype = freak_word_lit("bool");
                    vtype = freak_word_lit("b");
                }
            }
            freak_var_set(name, vtype);
            freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), ctype), freak_word_lit(" freak_")), name), freak_word_lit(" = ")), val), freak_word_lit(";")));
        }
        return;
    }
    if (freak_match_kw(freak_word_lit("say"))) {
        freak_eat_kw(freak_word_lit("say"));
        freak_skip_inline();
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("\""))) {
            pos += ((int64_t)1);
            freak_word str_val = freak_scan_string();
            if (freak_word_contains(str_val, freak_word_lit("{"))) {
                freak_word interp = freak_build_interpolation(str_val);
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_say(")), interp), freak_word_lit(");")));
            } else {
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_say(freak_word_lit(\"")), freak_c_escape(str_val)), freak_word_lit("\"));")));
            }
        } else {
            freak_word expr = freak_compile_expr();
            freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_say(")), expr), freak_word_lit(");")));
        }
        return;
    }
    if (freak_match_kw(freak_word_lit("give"))) {
        int64_t saved = pos;
        freak_eat_kw(freak_word_lit("give"));
        freak_skip_inline();
        if (freak_match_kw(freak_word_lit("back"))) {
            freak_eat_kw(freak_word_lit("back"));
            freak_skip_inline();
            if (freak_word_eq(freak_cur_ch(), freak_word_lit("}"))) {
                freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("return;")));
            } else {
                freak_word val = freak_compile_expr();
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("return ")), val), freak_word_lit(";")));
            }
            return;
        }
        pos = saved;
    }
    if (freak_match_kw(freak_word_lit("if"))) {
        freak_eat_kw(freak_word_lit("if"));
        freak_skip_inline();
        freak_word cond = freak_compile_expr();
        freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("if (")), cond), freak_word_lit(") {")));
        freak_compile_block();
        freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("}")));
        freak_skip_ws();
        bool checking_else = true;
        while (!((!checking_else))) {
            if (freak_match_kw(freak_word_lit("else"))) {
                freak_eat_kw(freak_word_lit("else"));
                freak_skip_inline();
                if (freak_match_kw(freak_word_lit("if"))) {
                    freak_eat_kw(freak_word_lit("if"));
                    freak_skip_inline();
                    freak_word elif_cond = freak_compile_expr();
                    freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("else if (")), elif_cond), freak_word_lit(") {")));
                    freak_compile_block();
                    freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("}")));
                    freak_skip_ws();
                } else {
                    freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("else {")));
                    freak_compile_block();
                    freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("}")));
                    checking_else = false;
                }
            } else {
                checking_else = false;
            }
        }
        return;
    }
    if (freak_match_kw(freak_word_lit("repeat"))) {
        freak_eat_kw(freak_word_lit("repeat"));
        freak_skip_inline();
        if (freak_match_kw(freak_word_lit("until"))) {
            freak_eat_kw(freak_word_lit("until"));
            freak_skip_inline();
            freak_word cond = freak_compile_expr();
            freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("while (!(")), cond), freak_word_lit(")) {")));
            freak_compile_block();
            freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("}")));
            return;
        }
        freak_word count_val = freak_compile_expr();
        freak_skip_inline();
        if (freak_match_kw(freak_word_lit("times"))) {
            freak_eat_kw(freak_word_lit("times"));
        }
        freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("for (int64_t __rep = 0; __rep < ")), count_val), freak_word_lit("; __rep++) {")));
        freak_compile_block();
        freak_emit_line(freak_word_concat(freak_ind(), freak_word_lit("}")));
        return;
    }
    if (freak_match_kw(freak_word_lit("task"))) {
        freak_eat_kw(freak_word_lit("task"));
        freak_skip_inline();
        freak_word fname = freak_scan_ident();
        freak_skip_inline();
        freak_word params = freak_word_lit("");
        int64_t pcount = ((int64_t)0);
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("("))) {
            pos += ((int64_t)1);
            freak_skip_inline();
            if ((!freak_word_eq(freak_cur_ch(), freak_word_lit(")")))) {
                bool pfin = false;
                while (!(pfin)) {
                    freak_word pname = freak_scan_ident();
                    freak_skip_inline();
                    freak_word pctype = freak_word_lit("int64_t");
                    if (freak_word_eq(freak_cur_ch(), freak_word_lit(":"))) {
                        pos += ((int64_t)1);
                        freak_skip_inline();
                        freak_word ptype = freak_scan_ident();
                        if (freak_word_eq(ptype, freak_word_lit("word"))) {
                            pctype = freak_word_lit("freak_word");
                        } else if (freak_word_eq(ptype, freak_word_lit("num"))) {
                            pctype = freak_word_lit("double");
                        } else if (freak_word_eq(ptype, freak_word_lit("bool"))) {
                            pctype = freak_word_lit("bool");
                        } else if (freak_word_eq(ptype, freak_word_lit("int"))) {
                            pctype = freak_word_lit("int64_t");
                        } else if (freak_word_eq(ptype, freak_word_lit("void"))) {
                            pctype = freak_word_lit("void");
                        } else {
                            pctype = ptype;
                        }
                    }
                    freak_skip_inline();
                    if ((pcount > ((int64_t)0))) {
                        params = freak_word_concat(params, freak_word_lit(", "));
                    }
                    params = freak_word_concat(freak_word_concat(freak_word_concat(params, pctype), freak_word_lit(" freak_")), pname);
                    pcount += ((int64_t)1);
                    if (freak_word_eq(freak_cur_ch(), freak_word_lit(","))) {
                        pos += ((int64_t)1);
                        freak_skip_inline();
                    } else {
                        pfin = true;
                    }
                }
            }
            if (freak_word_eq(freak_cur_ch(), freak_word_lit(")"))) {
                pos += ((int64_t)1);
            }
        }
        freak_skip_inline();
        freak_word rtype = freak_word_lit("void");
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("-"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit(">"))) {
                pos += ((int64_t)2);
                freak_skip_inline();
                freak_word rt = freak_scan_ident();
                if (freak_word_eq(rt, freak_word_lit("word"))) {
                    rtype = freak_word_lit("freak_word");
                } else if (freak_word_eq(rt, freak_word_lit("num"))) {
                    rtype = freak_word_lit("double");
                } else if (freak_word_eq(rt, freak_word_lit("bool"))) {
                    rtype = freak_word_lit("bool");
                } else if (freak_word_eq(rt, freak_word_lit("int"))) {
                    rtype = freak_word_lit("int64_t");
                } else if (freak_word_eq(rt, freak_word_lit("void"))) {
                    rtype = freak_word_lit("void");
                } else {
                    rtype = rt;
                }
            }
        }
        if (freak_word_eq(params, freak_word_lit(""))) {
            params = freak_word_lit("void");
        }
        fwd_decls = freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(fwd_decls, rtype), freak_word_lit(" freak_")), fname), freak_word_lit("(")), params), freak_word_lit(");\n"));
        freak_skip_inline();
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("="))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit(">"))) {
                pos += ((int64_t)2);
                freak_skip_inline();
                freak_word abody = freak_compile_expr();
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(rtype, freak_word_lit(" freak_")), fname), freak_word_lit("(")), params), freak_word_lit(") {")));
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_lit("    return "), abody), freak_word_lit(";")));
                freak_emit_line(freak_word_lit("}"));
                freak_emit_line(freak_word_lit(""));
                return;
            }
        }
        freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(rtype, freak_word_lit(" freak_")), fname), freak_word_lit("(")), params), freak_word_lit(") {")));
        freak_compile_block();
        freak_emit_line(freak_word_lit("}"));
        freak_emit_line(freak_word_lit(""));
        return;
    }
    if (freak_match_kw(freak_word_lit("shape"))) {
        freak_eat_kw(freak_word_lit("shape"));
        freak_skip_inline();
        freak_word sname = freak_scan_ident();
        freak_skip_ws();
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("{"))) {
            pos += ((int64_t)1);
            int64_t depth = ((int64_t)1);
            bool sfin = false;
            while (!(sfin)) {
                if (freak_at_end()) {
                    sfin = true;
                } else {
                    freak_word sc = freak_advance();
                    if (freak_word_eq(sc, freak_word_lit("{"))) {
                        depth += ((int64_t)1);
                    }
                    if (freak_word_eq(sc, freak_word_lit("}"))) {
                        depth -= ((int64_t)1);
                        if ((depth <= ((int64_t)0))) {
                            sfin = true;
                        }
                    }
                }
            }
        }
        return;
    }
    if (freak_is_alpha(freak_cur_ch())) {
        int64_t saved = pos;
        freak_word name = freak_scan_ident();
        freak_skip_inline();
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("+"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                pos += ((int64_t)2);
                freak_skip_inline();
                freak_word rhs = freak_compile_expr();
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_")), name), freak_word_lit(" += ")), rhs), freak_word_lit(";")));
                return;
            }
        }
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("-"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                pos += ((int64_t)2);
                freak_skip_inline();
                freak_word rhs = freak_compile_expr();
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_")), name), freak_word_lit(" -= ")), rhs), freak_word_lit(";")));
                return;
            }
        }
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("*"))) {
            if (freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("="))) {
                pos += ((int64_t)2);
                freak_skip_inline();
                freak_word rhs = freak_compile_expr();
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_")), name), freak_word_lit(" *= ")), rhs), freak_word_lit(";")));
                return;
            }
        }
        if (freak_word_eq(freak_cur_ch(), freak_word_lit("="))) {
            if ((!freak_word_eq(freak_ch_at(((int64_t)1)), freak_word_lit("=")))) {
                pos += ((int64_t)1);
                freak_skip_inline();
                freak_word rhs = freak_compile_expr();
                freak_emit_line(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_word_concat(freak_ind(), freak_word_lit("freak_")), name), freak_word_lit(" = ")), rhs), freak_word_lit(";")));
                return;
            }
        }
        pos = saved;
        freak_word expr = freak_compile_expr();
        if ((!freak_word_eq(expr, freak_word_lit("0")))) {
            freak_emit_line(freak_word_concat(freak_word_concat(freak_ind(), expr), freak_word_lit(";")));
        }
        return;
    }
    if ((!freak_at_end())) {
        pos += ((int64_t)1);
    }
}

static freak_word freak_compile_program(freak_word source) {
    src = source;
    pos = ((int64_t)0);
    cur_line = ((int64_t)1);
    indent_level = ((int64_t)0);
    output = freak_word_lit("");
    fwd_decls = freak_word_lit("");
    var_registry = freak_word_lit("");
    freak_word funcs = freak_word_lit("");
    freak_word main_body = freak_word_lit("");
    indent_level = ((int64_t)1);
    bool fin = false;
    while (!(fin)) {
        freak_skip_ws();
        if (freak_at_end()) {
            fin = true;
        } else if (freak_match_kw(freak_word_lit("task"))) {
            freak_word saved_out = output;
            output = freak_word_lit("");
            indent_level = ((int64_t)0);
            freak_compile_stmt();
            funcs = freak_word_concat(funcs, output);
            output = saved_out;
            indent_level = ((int64_t)1);
        } else if (freak_match_kw(freak_word_lit("shape"))) {
            freak_word saved_out = output;
            output = freak_word_lit("");
            freak_compile_stmt();
            output = saved_out;
        } else {
            freak_word saved_out = output;
            output = freak_word_lit("");
            freak_compile_stmt();
            main_body = freak_word_concat(main_body, output);
            output = saved_out;
        }
    }
    freak_word res = freak_word_lit("");
    res = freak_word_concat(res, freak_word_lit("#include \"freak_runtime.h\"\n"));
    res = freak_word_concat(res, freak_word_lit("\n"));
    if ((!freak_word_eq(fwd_decls, freak_word_lit("")))) {
        res = freak_word_concat(res, freak_word_lit("/* Forward declarations */\n"));
        res = freak_word_concat(res, fwd_decls);
        res = freak_word_concat(res, freak_word_lit("\n"));
    }
    if ((!freak_word_eq(funcs, freak_word_lit("")))) {
        res = freak_word_concat(res, funcs);
        res = freak_word_concat(res, freak_word_lit("\n"));
    }
    res = freak_word_concat(res, freak_word_lit("void freak_main(void) {\n"));
    res = freak_word_concat(res, main_body);
    res = freak_word_concat(res, freak_word_lit("}\n"));
    res = freak_word_concat(res, freak_word_lit("\n"));
    res = freak_word_concat(res, freak_word_lit("int main(int argc, char** argv) {\n"));
    res = freak_word_concat(res, freak_word_lit("    freak_argc = argc;\n"));
    res = freak_word_concat(res, freak_word_lit("    freak_argv = argv;\n"));
    res = freak_word_concat(res, freak_word_lit("    freak_main();\n"));
    res = freak_word_concat(res, freak_word_lit("    return 0;\n"));
    res = freak_word_concat(res, freak_word_lit("}\n"));
    return res;
}


int freak_main(int argc, char** argv) {
    output = freak_word_lit("");
    src = freak_word_lit("");
    pos = ((int64_t)0);
    cur_line = ((int64_t)1);
    indent_level = ((int64_t)0);
    var_registry = freak_word_lit("");
    fwd_decls = freak_word_lit("");
    input_file = freak_word_lit("tests/hello.fk");
    source = freak_fs_read(input_file);
    src_len = freak_word_length(source);
    c_result = freak_compile_program(source);
    output_c = freak_word_lit("tests/hello_self.c");
    freak_say(freak_word_lit("FREAK Self-Hosted Compiler v0.1.0"));
    freak_say(freak_word_lit("======================================"));
    freak_say(freak_interpolate("Compiling: %s", freak_word_to_cstr(input_file)));
    freak_say(freak_interpolate("Source loaded (%lld bytes)", (long long)src_len));
    freak_fs_write(output_c, c_result);
    freak_say(freak_interpolate("Wrote C: %s", freak_word_to_cstr(output_c)));
    freak_say(freak_word_lit(""));
    freak_say(freak_word_lit("Generated C:"));
    freak_say(freak_word_lit("======================================"));
    freak_say(c_result);
    freak_say(freak_word_lit("======================================"));
    freak_say(freak_word_lit("Bootstrap complete! M15 achieved."));
    return 0;
}

int main(int argc, char** argv) {
    freak_argc = argc;
    freak_argv = argv;
    (void)argc; (void)argv;
    return freak_main(argc, argv);
}
