# VESC Express Test Suite Makefile
# Refactored build system for improved maintainability

# Compiler settings
CC = gcc
CFLAGS = -Wall -Wextra -Werror -std=c99 -O2
INCLUDES = -I. -I../main -I../main/hwconf -I../main/config
LDFLAGS = -lm -lpthread

# Directories
FRAMEWORK_DIR = framework
INTERFACE_DIR = interface
UNIT_DIR = unit
INTEGRATION_DIR = integration
BUILD_DIR = build
BIN_DIR = bin

# Framework sources
FRAMEWORK_SOURCES = $(FRAMEWORK_DIR)/test_framework.c $(FRAMEWORK_DIR)/vesc_test_utils.c
FRAMEWORK_OBJECTS = $(FRAMEWORK_SOURCES:%.c=$(BUILD_DIR)/%.o)

# Test sources (organized by category)
INTERFACE_SOURCES = $(wildcard $(INTERFACE_DIR)/*.c)
UNIT_SOURCES = $(wildcard $(UNIT_DIR)/*.c)
INTEGRATION_SOURCES = $(wildcard $(INTEGRATION_DIR)/*.c)

# Test executables
INTERFACE_TARGETS = $(INTERFACE_SOURCES:$(INTERFACE_DIR)/%.c=$(BIN_DIR)/%)
UNIT_TARGETS = $(UNIT_SOURCES:$(UNIT_DIR)/%.c=$(BIN_DIR)/%)
INTEGRATION_TARGETS = $(INTEGRATION_SOURCES:$(INTEGRATION_DIR)/%.c=$(BIN_DIR)/%)

# All targets
ALL_TARGETS = $(INTERFACE_TARGETS) $(UNIT_TARGETS) $(INTEGRATION_TARGETS)

# Default target
.PHONY: all clean test test-interface test-unit test-integration help

all: directories framework $(ALL_TARGETS)

# Create necessary directories
directories:
	@mkdir -p $(BUILD_DIR)/$(FRAMEWORK_DIR)
	@mkdir -p $(BUILD_DIR)/$(INTERFACE_DIR)
	@mkdir -p $(BUILD_DIR)/$(UNIT_DIR)
	@mkdir -p $(BUILD_DIR)/$(INTEGRATION_DIR)
	@mkdir -p $(BIN_DIR)

# Build framework
framework: $(FRAMEWORK_OBJECTS)

# Generic rules for building objects
$(BUILD_DIR)/%.o: %.c
	@echo "Compiling $<..."
	@$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# Generic rules for building test executables
$(BIN_DIR)/%: $(INTERFACE_DIR)/%.c $(FRAMEWORK_OBJECTS)
	@echo "Building interface test $@..."
	@$(CC) $(CFLAGS) $(INCLUDES) $< $(FRAMEWORK_OBJECTS) $(LDFLAGS) -o $@

$(BIN_DIR)/%: $(UNIT_DIR)/%.c $(FRAMEWORK_OBJECTS)
	@echo "Building unit test $@..."
	@$(CC) $(CFLAGS) $(INCLUDES) $< $(FRAMEWORK_OBJECTS) $(LDFLAGS) -o $@

$(BIN_DIR)/%: $(INTEGRATION_DIR)/%.c $(FRAMEWORK_OBJECTS)
	@echo "Building integration test $@..."
	@$(CC) $(CFLAGS) $(INCLUDES) $< $(FRAMEWORK_OBJECTS) $(LDFLAGS) -o $@

# Test execution targets
test: test-interface test-unit test-integration

test-interface: $(INTERFACE_TARGETS)
	@echo "Running interface tests..."
	@for test in $(INTERFACE_TARGETS); do \
		echo "=== Running $$test ==="; \
		./$$test || exit 1; \
		echo ""; \
	done

test-unit: $(UNIT_TARGETS)
	@echo "Running unit tests..."
	@for test in $(UNIT_TARGETS); do \
		echo "=== Running $$test ==="; \
		./$$test || exit 1; \
		echo ""; \
	done

test-integration: $(INTEGRATION_TARGETS)
	@echo "Running integration tests..."
	@for test in $(INTEGRATION_TARGETS); do \
		echo "=== Running $$test ==="; \
		./$$test || exit 1; \
		echo ""; \
	done

# Individual test targets (for development)
.PHONY: bms lisp additional can uart bridge

bms: $(BIN_DIR)/test_bms_refactored
	@echo "Running BMS interface test..."
	@./$(BIN_DIR)/test_bms_refactored

lisp: $(BIN_DIR)/test_lisp_refactored
	@echo "Running LispBM interface test..."
	@./$(BIN_DIR)/test_lisp_refactored

additional: $(BIN_DIR)/test_additional_refactored
	@echo "Running additional features test..."
	@./$(BIN_DIR)/test_additional_refactored

# Static analysis
.PHONY: static-analysis
static-analysis:
	@echo "Running static analysis..."
	@echo "Checking for unsafe functions..."
	@! grep -r "strcpy\|strcat\|sprintf" $(INTERFACE_DIR) $(UNIT_DIR) $(INTEGRATION_DIR) 2>/dev/null || \
		(echo "⚠️  Unsafe string functions detected" && exit 1)
	@echo "✅ No unsafe string functions found"
	@echo "Checking for memory leaks..."
	@! grep -r "malloc\|calloc\|realloc" $(INTERFACE_DIR) $(UNIT_DIR) $(INTEGRATION_DIR) | grep -v "free" 2>/dev/null || \
		echo "⚠️  Potential memory leaks detected"
	@echo "✅ Static analysis passed"

# Code coverage (requires gcov)
.PHONY: coverage
coverage: CFLAGS += -fprofile-arcs -ftest-coverage
coverage: LDFLAGS += -lgcov --coverage
coverage: clean all test
	@echo "Generating coverage report..."
	@gcov $(BUILD_DIR)/**/*.gcda
	@echo "Coverage files generated: *.gcov"

# Performance profiling
.PHONY: profile
profile: CFLAGS += -pg
profile: LDFLAGS += -pg
profile: clean all
	@echo "Performance profiling enabled"
	@echo "Run tests and use 'gprof' to analyze performance"

# Documentation generation (requires doxygen)
.PHONY: docs
docs:
	@echo "Generating documentation..."
	@doxygen Doxyfile 2>/dev/null || echo "Doxygen not configured"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@rm -f *.gcov *.gcda *.gcno gmon.out

# Install test framework (for system-wide use)
.PHONY: install
install: framework
	@echo "Installing test framework..."
	@sudo cp $(FRAMEWORK_DIR)/*.h /usr/local/include/
	@sudo cp $(BUILD_DIR)/$(FRAMEWORK_DIR)/*.o /usr/local/lib/
	@echo "✅ Test framework installed"

# Help target
help:
	@echo "VESC Express Test Suite Build System"
	@echo "====================================="
	@echo ""
	@echo "Targets:"
	@echo "  all                 - Build all tests"
	@echo "  test                - Run all tests"
	@echo "  test-interface      - Run interface tests only"
	@echo "  test-unit           - Run unit tests only"  
	@echo "  test-integration    - Run integration tests only"
	@echo "  bms                 - Run BMS interface test"
	@echo "  lisp                - Run LispBM interface test"
	@echo "  additional          - Run additional features test"
	@echo "  static-analysis     - Run static code analysis"
	@echo "  coverage            - Generate code coverage report"
	@echo "  profile             - Build with profiling enabled"
	@echo "  docs                - Generate documentation"
	@echo "  clean               - Clean build artifacts"
	@echo "  install             - Install test framework system-wide"
	@echo "  help                - Show this help message"
	@echo ""
	@echo "Build Configuration:"
	@echo "  CC        = $(CC)"
	@echo "  CFLAGS    = $(CFLAGS)"
	@echo "  INCLUDES  = $(INCLUDES)"
	@echo "  LDFLAGS   = $(LDFLAGS)"
	@echo ""
	@echo "Directory Structure:"
	@echo "  framework/    - Shared test framework"
	@echo "  interface/    - Interface tests (BMS, LispBM, etc.)"
	@echo "  unit/         - Unit tests"
	@echo "  integration/  - Integration tests"
	@echo "  build/        - Build artifacts"
	@echo "  bin/          - Test executables"

# Dependencies
$(BUILD_DIR)/$(FRAMEWORK_DIR)/test_framework.o: $(FRAMEWORK_DIR)/test_framework.h
$(BUILD_DIR)/$(FRAMEWORK_DIR)/vesc_test_utils.o: $(FRAMEWORK_DIR)/vesc_test_utils.h $(FRAMEWORK_DIR)/test_framework.h

# Automatic dependency generation
-include $(BUILD_DIR)/**/*.d