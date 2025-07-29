# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Voidtime Chronoverse Hypothesis (VCH)** is a documentation-focused repository exploring theoretical cosmology hypotheses. The project investigates whether cosmic time flows at different rates across large-scale structures, particularly in cosmic voids.

## Repository Structure

- `docs/` - Contains all hypothesis modules (VCH-001 through VCH-005) and documentation
- `templates/` - Contains `vch_template.md` for creating new hypothesis modules
- `datasets/` - Directory for data files (currently empty)

## Content Architecture

### Module System
Each hypothesis is documented as a standalone module following the template structure:
- **Hypothesis**: Falsifiable statement
- **Motivation**: Context and anomalies addressed
- **Observables**: Measurable phenomena
- **Methodology**: Testing approaches
- **Expected Results**: Predictions if hypothesis is true
- **Falsifiability Criteria**: Conditions that would disprove the hypothesis
- **Data & Tools**: Relevant datasets and analysis platforms
- **Notes & Authors**: Additional context and attribution

### Current Modules
- VCH-001: Void Chronometer Hypothesis (time dilation in voids)
- VCH-002: Redshift Decomposition Model (alternative redshift components)
- VCH-003: CMB Void Entropy Signature (entropy patterns in CMB)
- VCH-004: High-z Galaxy Chronology Conflict (early galaxy formation)
- VCH-005: Sky Pattern Artifact Analysis (simulation detection)

## Common Tasks

### Creating New Modules
1. Use `templates/vch_template.md` as the starting point
2. Follow the established naming convention: `vch_XXX_descriptive_title.md`
3. Place in the `docs/` directory
4. Update `docs/vch_module_index.md` with the new module

### Documentation Standards
- All documentation uses Markdown format
- Maintain scientific neutrality and clarity
- Include proper citations when referencing studies
- Use the established emoji system for section headers
- License: CC BY 4.0 for documentation, Apache 2.0 for any code

### File Naming
- Hypothesis modules: `vch_###_descriptive_name.md`
- Use lowercase with underscores for consistency

## Contributing Process

The project follows a standard Git workflow:
1. Fork repository
2. Create feature branch with descriptive name (e.g., `vch-001-observation-extension`)
3. Make changes following the module template
4. Add contributor to `CONTRIBUTORS.md` if first contribution
5. Submit pull request with clear description

## Project Philosophy

This is a theoretical research documentation project focused on:
- Modular, falsifiable hypotheses
- Open scientific review and critique
- Observational relevance
- Collaborative refinement of ideas

The project values scientific rigor, testability, and welcomes contributions from diverse backgrounds including physicists, data scientists, and curious researchers.