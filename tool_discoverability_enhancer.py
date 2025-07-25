#!/usr/bin/env python3
"""
Tool Discoverability Enhancement Workflow
=========================================

Implements comprehensive tool discovery patterns for any specified tool using proven methodologies
from the ESP32-C6 VESC Express project. Creates a complete discovery ecosystem with:

- Convenience scripts with smart recommendations
- Usage analytics and tracking
- Claude Code slash command integration
- Comprehensive documentation suite
- Cross-platform compatibility
- Team onboarding materials

Author: Claude Code with proven ESP32 patterns
Date: 2025-07-24
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List
import logging

# Import the new modular components
from tool_discoverability_templates import ToolConfig
from tool_discoverability_generators import (
    ScriptGenerator,
    ConfigurationGenerator,
    SlashCommandGenerator,
    DocumentationGenerator
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ToolDiscoverabilityEnhancer:
    """
    Comprehensive tool discoverability enhancement workflow.

    Applies proven patterns from ESP32-C6 VESC Express project to any tool,
    creating a complete discovery ecosystem with analytics, documentation,
    and intelligent recommendations.
    """

    def __init__(self, tool_name: str, target_directory: str = "."):
        self.tool_name = tool_name
        self.target_directory = Path(target_directory).resolve()
        self.enhancement_config: Dict[str, Any] = {}
        self.patterns_applied: List[str] = []
        self.analytics_enabled = False

        # Ensure target directory exists
        self.target_directory.mkdir(exist_ok=True)

        logger.info(f"🎯 Initializing discoverability enhancement for '{tool_name}' in {self.target_directory}")

    async def enhance_tool_discoverability(self, options: Dict[str, bool]) -> Dict[str, Any]:
        """
        Main enhancement workflow that applies all requested patterns.

        Args:
            options: Dictionary of enhancement options

        Returns:
            Enhancement results with success metrics
        """
        logger.info(f"🚀 Starting tool discoverability enhancement for {self.tool_name}")
        start_time = time.time()

        results: Dict[str, Any] = {
            'tool_name': self.tool_name,
            'target_directory': str(self.target_directory),
            'patterns_applied': [],
            'files_created': [],
            'success': True,
            'errors': []
        }

        try:
            # Phase 1: Analysis & Planning
            if options.get('analyze', True):
                analysis_result = await self._analyze_tool_ecosystem()
                results['analysis'] = analysis_result

            # Phase 2: Core Infrastructure
            if options.get('convenience_script', False) or options.get('full', False):
                script_result = await self._create_convenience_script()
                results['convenience_script'] = script_result
                results['files_created'].extend(script_result.get('files_created', []))
                results['patterns_applied'].append('convenience_script')

            if options.get('analytics', False) or options.get('full', False):
                analytics_result = await self._implement_usage_analytics()
                results['analytics'] = analytics_result
                results['files_created'].extend(analytics_result.get('files_created', []))
                results['patterns_applied'].append('usage_analytics')

            if options.get('recommendations', False) or options.get('full', False):
                recommendations_result = await self._create_smart_recommendations()
                results['recommendations'] = recommendations_result
                results['files_created'].extend(recommendations_result.get('files_created', []))
                results['patterns_applied'].append('smart_recommendations')

            # Phase 3: Integration & Documentation
            if options.get('slash_commands', False) or options.get('full', False):
                slash_result = await self._create_slash_commands()
                results['slash_commands'] = slash_result
                results['files_created'].extend(slash_result.get('files_created', []))
                results['patterns_applied'].append('slash_commands')

            if options.get('docs', False) or options.get('full', False):
                docs_result = await self._generate_documentation_suite()
                results['documentation'] = docs_result
                results['files_created'].extend(docs_result.get('files_created', []))
                results['patterns_applied'].append('documentation')

            # Phase 4: Validation & Optimization
            if options.get('validate', False) or options.get('full', False):
                validation_result = await self._validate_implementation()
                results['validation'] = validation_result
                results['patterns_applied'].append('validation')

            # Calculate enhancement metrics
            enhancement_duration = time.time() - start_time
            results['enhancement_duration'] = round(enhancement_duration, 2)
            results['total_files_created'] = len(results['files_created'])
            results['patterns_count'] = len(results['patterns_applied'])

            logger.info(f"✅ Tool discoverability enhancement complete in {enhancement_duration:.2f}s")
            logger.info(f"📊 Applied {len(results['patterns_applied'])} patterns, created {len(results['files_created'])} files")

        except Exception as e:
            logger.error(f"❌ Enhancement failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    async def _analyze_tool_ecosystem(self) -> Dict[str, Any]:
        """Analyze the target tool's ecosystem and existing discovery mechanisms."""
        logger.info(f"🔍 Analyzing {self.tool_name} tool ecosystem")

        analysis = {
            'tool_name': self.tool_name,
            'existing_patterns': [],
            'opportunities': [],
            'recommended_enhancements': []
        }

        # Check for existing convenience scripts
        potential_scripts = [
            f"{self.tool_name}",
            f"{self.tool_name}.sh",
            f"{self.tool_name}_helper",
            f"run_{self.tool_name}",
            "Makefile"
        ]

        existing_scripts = []
        for script in potential_scripts:
            if (self.target_directory / script).exists():
                existing_scripts.append(script)
                analysis['existing_patterns'].append(f"convenience_script: {script}")

        # Check for existing documentation
        doc_files = [
            "README.md", "CLAUDE.md", "GETTING_STARTED.md",
            "QUICK_START.md", "TEAM_ONBOARDING.md"
        ]

        existing_docs = []
        for doc in doc_files:
            if (self.target_directory / doc).exists():
                existing_docs.append(doc)
                analysis['existing_patterns'].append(f"documentation: {doc}")

        # Check for slash commands
        slash_commands_dir = self.target_directory / ".claude" / "commands"
        if slash_commands_dir.exists():
            slash_files = list(slash_commands_dir.glob("*.md"))
            analysis['existing_patterns'].append(f"slash_commands: {len(slash_files)} commands")

        # Generate recommendations based on analysis
        if not existing_scripts:
            analysis['opportunities'].append("No convenience scripts detected")
            analysis['recommended_enhancements'].append("Create ultimate convenience script with smart recommendations")

        if not existing_docs:
            analysis['opportunities'].append("Limited documentation detected")
            analysis['recommended_enhancements'].append("Generate comprehensive documentation suite")

        if not slash_commands_dir.exists():
            analysis['opportunities'].append("No Claude Code integration detected")
            analysis['recommended_enhancements'].append("Implement slash command integration")

        # Check for analytics
        analytics_files = [".analytics.log", f".{self.tool_name}_analytics.log"]
        if not any((self.target_directory / f).exists() for f in analytics_files):
            analysis['opportunities'].append("No usage analytics detected")
            analysis['recommended_enhancements'].append("Implement usage analytics and smart recommendations")

        logger.info(f"📋 Analysis complete: {len(analysis['existing_patterns'])} existing patterns, {len(analysis['opportunities'])} opportunities")

        return analysis

    async def _create_convenience_script(self) -> Dict[str, Any]:
        """Create an ultimate convenience script with smart recommendations."""
        logger.info(f"🔧 Creating convenience script for {self.tool_name}")

        script_name = f"{self.tool_name}_ultimate"
        script_path = self.target_directory / script_name

        # Generate script content based on ESP32 patterns
        script_content = self._generate_convenience_script_content()

        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
        except Exception as e:
            logger.error(f"❌ Failed to write convenience script: {e}")
            raise

        # Make script executable
        script_path.chmod(0o755)

        logger.info(f"✅ Created convenience script: {script_path}")

        return {
            'success': True,
            'script_path': str(script_path),
            'script_name': script_name,
            'files_created': [str(script_path)],
            'features': [
                'Smart environment detection',
                'Context-aware recommendations',
                'Usage analytics integration',
                'Visual branding and UX',
                '15+ command categories',
                'Cross-platform compatibility'
            ]
        }

    def _generate_convenience_script_content(self) -> str:
        """Generate convenience script content using modular templates."""
        try:
            config = ToolConfig.from_tool_name(self.tool_name)
            generator = ScriptGenerator(config)
            return generator.generate_convenience_script()
        except Exception as e:
            logger.error(f"❌ Error generating convenience script content: {e}")
            raise

    async def _implement_usage_analytics(self) -> Dict[str, Any]:
        """Implement usage analytics and tracking based on proven patterns."""
        logger.info(f"📊 Implementing usage analytics for {self.tool_name}")

        # Create analytics report script
        analytics_script_path = self.target_directory / f"{self.tool_name}_analytics_report.sh"

        analytics_content = self._generate_analytics_script_content()

        with open(analytics_script_path, 'w') as f:
            f.write(analytics_content)

        analytics_script_path.chmod(0o755)

        logger.info(f"✅ Created analytics script: {analytics_script_path}")

        return {
            'success': True,
            'analytics_script': str(analytics_script_path),
            'files_created': [str(analytics_script_path)],
            'features': [
                'Real-time usage tracking',
                'Command categorization',
                'Smart recommendation engine',
                'Performance metrics',
                'Trend analysis',
                'Export capabilities'
            ]
        }

    def _generate_analytics_script_content(self) -> str:
        """Generate analytics script using modular templates."""
        try:
            config = ToolConfig.from_tool_name(self.tool_name)
            generator = ScriptGenerator(config)
            return generator.generate_analytics_script()
        except Exception as e:
            logger.error(f"❌ Error generating analytics script content: {e}")
            raise

    async def _create_smart_recommendations(self) -> Dict[str, Any]:
        """Create smart recommendation system using modular templates."""
        logger.info(f"🤖 Creating smart recommendation system for {self.tool_name}")

        try:
            # Generate configuration using templates
            config = ToolConfig.from_tool_name(self.tool_name)
            generator = ConfigurationGenerator(config)
            recommendations_config = generator.generate_recommendations_config()

            config_path = self.target_directory / f"{self.tool_name}_recommendations.json"
            with open(config_path, 'w') as f:
                json.dump(recommendations_config, f, indent=2)

            logger.info(f"✅ Created recommendation system: {config_path}")

            return {
                'success': True,
                'config_path': str(config_path),
                'files_created': [str(config_path)],
                'features': [
                    'Context-aware analysis',
                    'Priority-based recommendations',
                    'Learning from usage patterns',
                    'Performance-driven suggestions',
                    'Error-based guidance'
                ]
            }
        except Exception as e:
            logger.error(f"❌ Error creating recommendations: {e}")
            raise

    async def _create_slash_commands(self) -> Dict[str, Any]:
        """Create Claude Code slash command integration using modular templates."""
        logger.info(f"⚡ Creating slash command integration for {self.tool_name}")

        try:
            # Create .claude/commands directory
            commands_dir = self.target_directory / ".claude" / "commands"
            commands_dir.mkdir(parents=True, exist_ok=True)

            # Generate slash commands using templates
            config = ToolConfig.from_tool_name(self.tool_name)
            generator = SlashCommandGenerator(config)
            slash_commands = generator.get_default_commands()

            files_created = []

            for cmd_name, cmd_description in slash_commands:
                cmd_file = commands_dir / f"{self.tool_name}-{cmd_name}.md"
                cmd_content = generator.generate_slash_command_content(cmd_name, cmd_description)

                with open(cmd_file, 'w') as f:
                    f.write(cmd_content)

                files_created.append(str(cmd_file))
                logger.debug(f"Created slash command: /{self.tool_name}-{cmd_name}")

            logger.info(f"✅ Created {len(slash_commands)} slash commands in {commands_dir}")

            return {
                'success': True,
                'commands_directory': str(commands_dir),
                'commands_created': len(slash_commands),
                'files_created': files_created,
                'slash_commands': [f"/{self.tool_name}-{cmd}" for cmd, _ in slash_commands]
            }
        except Exception as e:
            logger.error(f"❌ Error creating slash commands: {e}")
            raise

    async def _generate_documentation_suite(self) -> Dict[str, Any]:
        """Generate comprehensive documentation suite using modular templates."""
        logger.info(f"📚 Generating documentation suite for {self.tool_name}")

        try:
            config = ToolConfig.from_tool_name(self.tool_name)
            generator = DocumentationGenerator(config)

            docs_to_create = [
                ('TEAM_ONBOARDING.md', generator.generate_team_onboarding_doc),
                ('TOOL_DISCOVERY_GUIDE.md', generator.generate_discovery_guide_doc),
                ('CROSS_PLATFORM_COMPATIBILITY.md', generator.generate_compatibility_doc),
                ('ANALYTICS_AND_OPTIMIZATION.md', generator.generate_analytics_doc)
            ]

            files_created = []

            for doc_name, generator_func in docs_to_create:
                doc_path = self.target_directory / doc_name
                doc_content = generator_func()

                with open(doc_path, 'w') as f:
                    f.write(doc_content)

                files_created.append(str(doc_path))
                logger.debug(f"Created documentation: {doc_name}")

            logger.info(f"✅ Generated {len(docs_to_create)} documentation files")

            return {
                'success': True,
                'files_created': files_created,
                'documentation_types': [doc[0] for doc in docs_to_create],
                'features': [
                    'Team onboarding guide',
                    'Tool discovery methodology',
                    'Cross-platform compatibility',
                    'Analytics and optimization'
                ]
            }

        except Exception as e:
            logger.error(f"❌ Error generating documentation suite: {e}")
            return {
                'success': False,
                'error': str(e),
                'files_created': []
            }

    async def _validate_implementation(self) -> Dict[str, Any]:
        """Validate implementation and fix common issues."""
        logger.info(f"🔍 Validating implementation for {self.tool_name}")

        validation_results = {
            'success': True,
            'files_validated': 0,
            'issues_found': [],
            'fixes_applied': []
        }

        try:
            import stat

            # Check all files in target directory
            for file_path in self.target_directory.rglob('*'):
                if file_path.is_file():
                    validation_results['files_validated'] += 1

                    # Fix script permissions
                    if file_path.suffix == '' and file_path.name.endswith('_ultimate'):
                        try:
                            file_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
                            validation_results['fixes_applied'].append(f"Fixed permissions: {file_path.name}")
                        except Exception as e:
                            validation_results['issues_found'].append(f"Permission fix failed for {file_path.name}: {e}")

                    # Validate script files
                    elif file_path.suffix == '.sh':
                        try:
                            file_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
                            validation_results['fixes_applied'].append(f"Fixed permissions: {file_path.name}")
                        except Exception as e:
                            validation_results['issues_found'].append(f"Permission fix failed for {file_path.name}: {e}")

            logger.info(f"✅ Validated {validation_results['files_validated']} files")

            if validation_results['issues_found']:
                validation_results['success'] = False
                logger.warning(f"⚠️ Found {len(validation_results['issues_found'])} validation issues")

            return validation_results

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'files_validated': validation_results['files_validated'],
                'issues_found': validation_results['issues_found'],
                'fixes_applied': validation_results['fixes_applied']
            }


async def main():
    """Main CLI interface for tool discoverability enhancement."""
    parser = argparse.ArgumentParser(
        description='Tool Discoverability Enhancement Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python tool_discoverability_enhancer.py fastmcp --full
  python tool_discoverability_enhancer.py openocd --analytics --docs
  python tool_discoverability_enhancer.py npm --convenience-script --validate
        '''
    )

    parser.add_argument('tool_name', help='Name of the tool to enhance')
    parser.add_argument('--target-directory', default='.', help='Target directory for enhancement')
    parser.add_argument('--full', action='store_true', help='Complete implementation (all patterns)')
    parser.add_argument('--analytics', action='store_true', help='Usage analytics and smart recommendations')
    parser.add_argument('--docs', action='store_true', help='Documentation suite generation')
    parser.add_argument('--convenience-script', action='store_true', help='Ultimate tool wrapper creation')
    parser.add_argument('--slash-commands', action='store_true', help='Claude Code integration')
    parser.add_argument('--recommendations', action='store_true', help='Smart recommendation system')
    parser.add_argument('--validate', action='store_true', help='Test implementation and fix issues')
    parser.add_argument('--dry-run', action='store_true', help='Show implementation plan without changes')

    args = parser.parse_args()

    if args.dry_run:
        print(f"🔍 DRY RUN: Tool discoverability enhancement plan for '{args.tool_name}'")
        print(f"📁 Target directory: {args.target_directory}")
        print(f"🎯 Options: {vars(args)}")
        return 0

    # Create enhancer instance
    enhancer = ToolDiscoverabilityEnhancer(args.tool_name, args.target_directory)

    # Run enhancement workflow
    options = {
        'full': args.full,
        'analytics': args.analytics,
        'docs': args.docs,
        'convenience_script': args.convenience_script,
        'slash_commands': args.slash_commands,
        'recommendations': args.recommendations,
        'validate': args.validate
    }

    # If no specific options, default to analyze
    if not any(options.values()):
        options['analyze'] = True

    try:
        results = await enhancer.enhance_tool_discoverability(options)

        # Print results
        print(json.dumps(results, indent=2))

        if results['success']:
            print(f"\n✅ Tool discoverability enhancement complete for '{args.tool_name}'!")
            print(f"📊 Applied {results['patterns_count']} patterns, created {results['total_files_created']} files")
            print(f"⏱️  Enhancement completed in {results['enhancement_duration']}s")
            return 0
        else:
            print(f"\n❌ Enhancement failed with {len(results['errors'])} errors")
            return 1

    except Exception as e:
        logger.error(f"❌ Enhancement failed: {e}")
        return 1

if __name__ == '__main__':
    import asyncio
    sys.exit(asyncio.run(main()))
