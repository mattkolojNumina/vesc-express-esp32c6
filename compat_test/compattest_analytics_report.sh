#!/bin/bash
# Compattest Tool Usage Analytics Report Generator
# Based on proven ESP32-C6 VESC Express patterns

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_analytics_logo() {
    echo -e "${CYAN}"
    echo "📊 Compattest Tool Usage Analytics"
    echo "═══════════════════════════════════════"
    echo -e "${NC}"
}

generate_analytics_report() {
    print_analytics_logo

    if [ ! -f ".compattest_analytics.log" ]; then
        echo -e "${YELLOW}⚠️  No analytics data found. Use ./compattest_ultimate commands to generate usage data.${NC}"
        echo ""
        echo "Commands that generate analytics:"
        echo "  ./compattest_ultimate setup, start, dev, debug"
        echo "  ./compattest_ultimate suggest, discover, analyze"
        return 1
    fi

    total_commands=$(wc -l < .compattest_analytics.log)
    echo -e "${GREEN}📈 Total Commands Used: $total_commands${NC}"
    echo ""

    echo -e "${BLUE}🔝 Most Popular Commands:${NC}"
    # Extract command names and count occurrences
    if command -v awk &> /dev/null; then
        awk '{print $4}' .compattest_analytics.log | sort | uniq -c | sort -nr | head -5 | while read count cmd; do
            echo "  $cmd: $count uses"
        done
    else
        echo "  (awk not available for detailed analysis)"
    fi
    echo ""

    echo -e "${BLUE}📅 Usage Timeline (Last 10 entries):${NC}"
    tail -10 .compattest_analytics.log | while read line; do
        echo "  $line"
    done
    echo ""

    echo -e "${BLUE}📊 Command Categories:${NC}"
    dev_commands=$(grep -E "(start|setup|dev|check)" .compattest_analytics.log 2>/dev/null | wc -l)
    debug_commands=$(grep -E "(debug|troubleshoot|analyze)" .compattest_analytics.log 2>/dev/null | wc -l)
    discovery_commands=$(grep -E "(suggest|discover|analytics)" .compattest_analytics.log 2>/dev/null | wc -l)

    echo "  🔨 Development: $dev_commands commands"
    echo "  🐛 Debugging: $debug_commands commands"
    echo "  🔍 Discovery: $discovery_commands commands"
    echo ""

    # Calculate usage trends
    today_count=$(grep "$(date '+%Y-%m-%d')" .compattest_analytics.log 2>/dev/null | wc -l)
    echo -e "${BLUE}📅 Today's Activity: $today_count commands${NC}"

    if [ "$today_count" -gt 5 ]; then
        echo -e "${GREEN}🎉 Active development session detected!${NC}"
    elif [ "$today_count" -gt 0 ]; then
        echo -e "${YELLOW}🔧 Some development activity today${NC}"
    fi

    echo ""
    echo -e "${CYAN}💡 Recommendations based on usage:${NC}"

    if [ "$dev_commands" -gt "$debug_commands" ]; then
        echo "  • Consider using more debugging tools for better development workflow"
        echo "  • Try: ./compattest_ultimate debug for interactive debugging sessions"
    fi

    if [ "$discovery_commands" -lt 3 ]; then
        echo "  • Explore more tools with: ./compattest_ultimate discover"
        echo "  • Get smart recommendations with: ./compattest_ultimate suggest"
    fi

    echo ""
    echo -e "${BLUE}To clear analytics: rm .compattest_analytics.log${NC}"
}

case "$1" in
    "clear")
        if [ -f ".compattest_analytics.log" ]; then
            rm .compattest_analytics.log
            echo -e "${GREEN}✅ Analytics data cleared${NC}"
        else
            echo -e "${YELLOW}No analytics data to clear${NC}"
        fi
        ;;
    "export")
        if [ -f ".compattest_analytics.log" ]; then
            export_file="compattest_analytics_$(date '+%Y%m%d_%H%M%S').log"
            cp .compattest_analytics.log "$export_file"
            echo -e "${GREEN}✅ Analytics exported to: $export_file${NC}"
        else
            echo -e "${YELLOW}No analytics data to export${NC}"
        fi
        ;;
    *)
        generate_analytics_report
        ;;
esac
