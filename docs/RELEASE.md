# Release Process

This project includes automated release scripts to help create tagged releases.

## Release Scripts

### 1. Basic Release (`release.sh`)
Creates a git tag and pushes it to origin.

```bash
./scripts/release.sh
```

**Features:**
- Prompts for version (vX.Y.Z format)
- Prompts for release title and description
- Creates annotated git tag
- Pushes tag and branch to origin
- Validates working directory is clean
- Prevents duplicate tags

### 2. GitHub Release (`release-github.sh`)
Enhanced version that can also create GitHub releases.

```bash
./scripts/release-github.sh
```

**Additional Features:**
- Shows commits since last tag
- Auto-generates changelog from commit messages
- Creates GitHub release (if GitHub CLI is installed)
- Supports release types (bug fix, feature, breaking change)
- Handles pre-releases (alpha, beta, rc)

### 3. Clean Release (`release-clean.sh`) **[RECOMMENDED]**
Creates a clean release package with only runtime files.

```bash
./scripts/release-clean.sh
```

**Features:**
- All GitHub release features
- **Creates clean package with only necessary files**
- Uses `.releasefiles` configuration to define included files
- **Generates downloadable zip archive**
- Excludes development files, scripts, and build artifacts
- Creates release-specific README with installation instructions
- **Perfect for distribution to end users**

## Prerequisites

### For Basic Releases
- Git repository
- Clean working directory
- Push access to origin

### For GitHub Releases
- All basic requirements
- GitHub CLI (`gh`) installed and authenticated
- Repository hosted on GitHub

## Version Format

Use semantic versioning: `vMAJOR.MINOR.PATCH`

Examples:
- `v1.0.0` - Initial release
- `v1.0.1` - Bug fix
- `v1.1.0` - New feature
- `v2.0.0` - Breaking change
- `v1.0.0-beta.1` - Pre-release

## Release Types

The GitHub release script supports categorizing releases:

1. 🐛 **Bug fix (patch)** - Backwards compatible bug fixes
2. ✨ **New feature (minor)** - Backwards compatible functionality
3. 💥 **Breaking change (major)** - Incompatible API changes
4. 🏷️ **Other** - Documentation, refactoring, etc.

## Workflow

1. **Prepare release**
   - Ensure all changes are committed
   - Update version numbers if needed
   - Write release notes

2. **Run release script**
   ```bash
   ./scripts/release-github.sh
   ```

3. **Follow prompts**
   - Enter version number
   - Enter release title
   - Choose release type
   - Add description
   - Review generated changelog

4. **Confirm and publish**
   - Review summary
   - Confirm to proceed
   - Optionally create GitHub release

## Managing Releases

### View Releases
```bash
# List all tags
git tag -l

# View tag details
git show v1.0.0

# List GitHub releases (requires gh CLI)
gh release list
```

### Delete Release (if needed)
```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Delete GitHub release (requires gh CLI)
gh release delete v1.0.0
```

## Release Configuration

### `.releasefiles` Configuration
The clean release script uses a `.releasefiles` file to define which files to include in the release package:

```
# Files to include in release
streamlit_app.py
requirements.txt
README.md
LICENSE
example_workout.json
example_pace.json
data/
```

**Format:**
- One file/directory per line
- Supports glob patterns (e.g., `*.json`)
- Lines starting with `#` are comments
- Empty lines are ignored

**Default Files (if no `.releasefiles`):**
- `streamlit_app.py`
- `requirements.txt`
- `README.md`
- `LICENSE`
- `*.json`

## Best Practices

1. **Use clean releases for distribution** (`release-clean.sh`)
2. **Always create releases from main/develop branch**
3. **Ensure working directory is clean**
4. **Test thoroughly before releasing**
5. **Write clear, descriptive release notes**
6. **Follow semantic versioning**
7. **Include breaking changes in major versions**
8. **Use pre-releases for testing (alpha, beta, rc)**
9. **Test the release archive before distribution**