#include "freak_runtime.h"

void freak_main(void) {
    freak_word freak_name = freak_word_lit("Takeru");
    int64_t freak_power = ((int64_t)9001);
    freak_say(freak_interpolate("Hello from FREAK! %s has power %lld.", freak_word_to_cstr(freak_name), (long long)freak_power));
}

int main(int argc, char** argv) {
    freak_argc = argc;
    freak_argv = argv;
    freak_main();
    return 0;
}
