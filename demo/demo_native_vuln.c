// filename: demo_native_vuln.c
// language: C — illustrative snippets only (do NOT compile/run)


// Buffer overflow pattern (illustration)
void copy_user_input(const char *userInput) {
char buf[16];
// UNSAFE: no bounds checking — demonstration only
// strcpy(buf, userInput); // DO NOT RUN
}


// Unsafe temporary file usage (path traversal demonstration)
void save_file_demo(const char *filename) {
// naive path join
// char path[256];
// snprintf(path, sizeof(path), "/var/data/%s", filename);
// fopen(path, "w"); // simulated
}