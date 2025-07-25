#!/bin/bash
# VESC Express Tool Usage Analytics Report Generator

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_analytics_logo() {
    echo -e "${CYAN}"
    echo "📊 VESC Express Tool Usage Analytics"
    echo "═══════════════════════════════════════"
    echo -e "${NC}"
}

generate_analytics_report() {
    print_analytics_logo
    
    if [ ! -f ".vesc_analytics.log" ]; then
        echo -e "${YELLOW}⚠️  No analytics data found. Use ./vesc commands to generate usage data.${NC}"
        echo ""
        echo "Commands that generate analytics:"
        echo "  ./vesc setup, ./vesc build, ./vesc dev, ./vesc debug"
        echo "  ./vesc suggest, ./vesc tools, ./vesc discover"
        return 1
    fi
    
    local total_commands=$(wc -l < .vesc_analytics.log)
    echo -e "${GREEN}📈 Total Commands Used: $total_commands${NC}"
    echo ""
    
    echo -e "${BLUE}🔝 Most Popular Commands:${NC}"
    # Extract command names and count occurrences
    if command -v awk &> /dev/null; then
        awk '{print $4}' .vesc_analytics.log | sort | uniq -c | sort -nr | head -5 | while read count cmd; do
            echo "  $cmd: $count uses"
        done
    else
        echo "  (awk not available for detailed analysis)"
    fi
    echo ""
    
    echo -e "${BLUE}📅 Usage Timeline (Last 10 entries):${NC}"
    tail -10 .vesc_analytics.log | while read line; do
        echo "  $line"
    done
    echo ""
    
    echo -e "${BLUE}📊 Command Categories:${NC}"
    dev_commands=$(grep -E "(build|flash|dev|monitor)" .vesc_analytics.log 2>/dev/null | wc -l)
    debug_commands=$(grep -E "(debug|troubleshoot|analyze)" .vesc_analytics.log 2>/dev/null | wc -l)
    discovery_commands=$(grep -E "(suggest|tools|discover)" .vesc_analytics.log 2>/dev/null | wc -l)
    
    echo "  🔨 Development: $dev_commands commands"
    echo "  🐛 Debugging: $debug_commands commands"
    echo "  🔍 Discovery: $discovery_commands commands"
    echo ""
    
    # Calculate usage trends
    today_count=$(grep "$(date '+%Y-%m-%d')" .vesc_analytics.log 2>/dev/null | wc -l)
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
        echo "  • Try: ./vesc debug for interactive debugging sessions"
    fi
    
    if [ "$discovery_commands" -lt 3 ]; then
        echo "  • Explore more tools with: ./vesc discover"
        echo "  • Get smart recommendations with: ./vesc suggest"
    fi
    
    echo ""
    echo -e "${BLUE}To clear analytics: rm .vesc_analytics.log${NC}"
}

case "$1" in
    "clear")
        if [ -f ".vesc_analytics.log" ]; then
            rm .vesc_analytics.log
            echo -e "${GREEN}✅ Analytics data cleared${NC}"
        else
            echo -e "${YELLOW}No analytics data to clear${NC}"
        fi
        ;;
    "export")
        if [ -f ".vesc_analytics.log" ]; then
            export_file="vesc_analytics_$(date '+%Y%m%d_%H%M%S').log"
            cp .vesc_analytics.log "$export_file"
            echo -e "${GREEN}✅ Analytics exported to: $export_file${NC}"
        else
            echo -e "${YELLOW}No analytics data to export${NC}"
        fi
        ;;
    *)
        generate_analytics_report
        ;;
esac