#!/bin/bash

# AMRAP Calculator Clean Release Script
# Creates a release with only necessary runtime files

set -e  # Exit on any error

echo "🚀 AMRAP Calculator Clean Release Script"
echo "========================================"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Error: Working directory is not clean. Please commit or stash changes first."
    git status --short
    exit 1
fi

# Check if gh CLI is available
GH_AVAILABLE=false
if command -v gh &> /dev/null; then
    GH_AVAILABLE=true
    echo "✅ GitHub CLI detected"
else
    echo "⚠️  GitHub CLI not found. Will create git tag only."
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Get the last tag (if any)
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "No previous tags")
echo "🏷️  Last tag: $LAST_TAG"

echo ""
echo "📝 Release Information"
echo "---------------------"

# Prompt for version
while true; do
    read -p "Enter version (e.g., v1.0.0, v0.1.2): " VERSION
    if [[ $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        break
    else
        echo "❌ Invalid version format. Please use vX.Y.Z (e.g., v1.0.0)"
    fi
done

# Check if tag already exists
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "❌ Error: Tag $VERSION already exists"
    exit 1
fi

# Prompt for release title
read -p "Enter release title: " RELEASE_TITLE

# Prompt for release type
echo ""
echo "Select release type:"
echo "1) 🐛 Bug fix (patch)"
echo "2) ✨ New feature (minor)"
echo "3) 💥 Breaking change (major)"
echo "4) 🏷️  Other"
read -p "Choose (1-4): " RELEASE_TYPE

case $RELEASE_TYPE in
    1) TYPE_EMOJI="🐛"; TYPE_TEXT="Bug Fix" ;;
    2) TYPE_EMOJI="✨"; TYPE_TEXT="New Feature" ;;
    3) TYPE_EMOJI="💥"; TYPE_TEXT="Breaking Change" ;;
    4) TYPE_EMOJI="🏷️"; TYPE_TEXT="Release" ;;
    *) TYPE_EMOJI="🏷️"; TYPE_TEXT="Release" ;;
esac

# Prompt for release description
echo ""
echo "Enter release description (press Ctrl+D when done):"
RELEASE_DESCRIPTION=$(cat)

echo ""
echo "📋 Release Summary"
echo "------------------"
echo "Version: $VERSION"
echo "Title: $TYPE_EMOJI $RELEASE_TITLE"
echo "Type: $TYPE_TEXT"
echo "Branch: $CURRENT_BRANCH"
echo "Description:"
echo "$RELEASE_DESCRIPTION"

echo ""
read -p "🤔 Proceed with release? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    exit 1
fi

echo ""
echo "🔄 Creating clean release..."

# Update VERSION file
echo "📝 Updating VERSION file..."
VERSION_NUM=${VERSION#v}  # Remove 'v' prefix for VERSION file
echo "$VERSION_NUM" > VERSION
git add VERSION
git commit -m "Bump version to $VERSION"
echo "✅ VERSION file updated and committed"

# Create temporary directory for release files
RELEASE_DIR="release-$VERSION"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

echo "📦 Copying release files..."

# Read release files list
if [[ -f ".releasefiles" ]]; then
    echo "📋 Using .releasefiles configuration"
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        
        # Copy files/directories
        if [[ -e "$line" ]]; then
            echo "  ✅ $line"
            # Create parent directory structure in release dir
            if [[ -d "$line" ]]; then
                cp -r "$line" "$RELEASE_DIR/"
            else
                parent_dir=$(dirname "$line")
                if [[ "$parent_dir" != "." ]]; then
                    mkdir -p "$RELEASE_DIR/$parent_dir"
                fi
                cp "$line" "$RELEASE_DIR/$line"
            fi
        else
            echo "  ⚠️  $line (not found)"
        fi
    done < .releasefiles
else
    echo "📋 No .releasefiles found, using defaults"
    # Default files to include
    DEFAULT_FILES=(
        "streamlit_app.py"
        "requirements.txt"
        "README.md"
        "LICENSE"
        "*.json"
    )
    
    for file in "${DEFAULT_FILES[@]}"; do
        if ls $file 1> /dev/null 2>&1; then
            echo "  ✅ $file"
            cp $file "$RELEASE_DIR/"
        fi
    done
fi

# Create a simple README for the release
cat > "$RELEASE_DIR/RELEASE_README.md" << EOF
# AMRAP Calculator $VERSION

$TYPE_EMOJI **$RELEASE_TITLE**

$RELEASE_DESCRIPTION

## Quick Start

1. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. Run the application:
   \`\`\`bash
   streamlit run streamlit_app.py
   \`\`\`

## Release Information

- **Version**: $VERSION
- **Release Date**: $(date +"%Y-%m-%d")
- **Source**: Generated from $CURRENT_BRANCH branch

For full documentation and source code, visit the main repository.
EOF

echo "✅ Created release package in $RELEASE_DIR/"

# Create a zip archive
ARCHIVE_NAME="amrap-calculator-$VERSION.zip"
echo "📦 Creating archive: $ARCHIVE_NAME"
cd "$RELEASE_DIR"
zip -r "../$ARCHIVE_NAME" . > /dev/null
cd ..

echo "✅ Created archive: $ARCHIVE_NAME"

# Create the tag on current branch
git tag -a "$VERSION" -m "$TYPE_EMOJI $RELEASE_TITLE

$RELEASE_DESCRIPTION

Release package: $ARCHIVE_NAME"

echo "✅ Created tag: $VERSION"

# Push the tag to origin
echo "📤 Pushing tag to origin..."
git push origin "$VERSION"
echo "✅ Tag pushed to origin"

# Create GitHub release with the archive
if [[ "$GH_AVAILABLE" = true ]]; then
    echo ""
    read -p "🐙 Create GitHub release with archive? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "📤 Creating GitHub release with archive..."
        
        # Determine if it's a prerelease
        PRERELEASE_FLAG=""
        if [[ $VERSION =~ (alpha|beta|rc) ]]; then
            PRERELEASE_FLAG="--prerelease"
        fi
        
        FULL_NOTES="$RELEASE_DESCRIPTION

## Installation

1. Download and extract \`$ARCHIVE_NAME\`
2. Install dependencies: \`pip install -r requirements.txt\`
3. Run: \`streamlit run streamlit_app.py\`

## Files Included

$(cd "$RELEASE_DIR" && find . -type f | sort | sed 's/^/- /')"
        
        gh release create "$VERSION" \
            --title "$TYPE_EMOJI $RELEASE_TITLE" \
            --notes "$FULL_NOTES" \
            "$ARCHIVE_NAME" \
            $PRERELEASE_FLAG
        
        echo "✅ GitHub release created with archive"
    fi
fi

echo ""
echo "🎉 Clean release $VERSION created successfully!"
echo ""
echo "📌 What was created:"
echo "  • Git tag: $VERSION"
echo "  • Release directory: $RELEASE_DIR/"
echo "  • Release archive: $ARCHIVE_NAME"
if [[ "$GH_AVAILABLE" = true ]]; then
    echo "  • GitHub release (if requested)"
fi
echo ""
echo "📦 Release contains only runtime files:"
echo "$(cd "$RELEASE_DIR" && find . -type f | sort | sed 's/^/  • /')"
echo ""
echo "🔗 Next steps:"
echo "  • Test the release archive"
echo "  • Distribute $ARCHIVE_NAME"
echo "  • Clean up: rm -rf $RELEASE_DIR $ARCHIVE_NAME"
echo ""
echo "🗑️  Cleanup command:"
echo "  rm -rf $RELEASE_DIR $ARCHIVE_NAME"