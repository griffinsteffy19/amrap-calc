#!/bin/bash

# AMRAP Calculator GitHub Release Script
# Creates a tagged release and optionally creates a GitHub release

set -e  # Exit on any error

echo "🚀 AMRAP Calculator GitHub Release Script"
echo "========================================="

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

# Show recent commits since last tag
if [[ "$LAST_TAG" != "No previous tags" ]]; then
    echo ""
    echo "📋 Commits since $LAST_TAG:"
    git log --oneline --decorate --graph "$LAST_TAG"..HEAD || echo "No commits since last tag"
fi

echo ""
echo "📝 Release Information"
echo "---------------------"

# Prompt for version
while true; do
    read -p "Enter version (e.g., v1.0.0, v0.1.2): " .VERSION
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

# Auto-generate changelog if possible
CHANGELOG=""
if [[ "$LAST_TAG" != "No previous tags" ]]; then
    echo ""
    read -p "📜 Generate changelog from commits? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        CHANGELOG=$(git log --pretty=format:"- %s" "$LAST_TAG"..HEAD | head -20)
        if [[ -n "$CHANGELOG" ]]; then
            echo ""
            echo "Generated changelog:"
            echo "$CHANGELOG"
            echo ""
            read -p "📝 Include this changelog? (Y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                CHANGELOG=""
            fi
        fi
    fi
fi

# Combine description and changelog
FULL_DESCRIPTION="$RELEASE_DESCRIPTION"
if [[ -n "$CHANGELOG" ]]; then
    FULL_DESCRIPTION="$RELEASE_DESCRIPTION
    
    ## Changes
    $CHANGELOG"
fi

echo ""
echo "📋 Release Summary"
echo "------------------"
echo "Version: $VERSION"
echo "Title: $TYPE_EMOJI $RELEASE_TITLE"
echo "Type: $TYPE_TEXT"
echo "Branch: $CURRENT_BRANCH"
echo "Description:"
echo "$FULL_DESCRIPTION"

echo ""
read -p "🤔 Proceed with release? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    exit 1
fi

echo ""
echo "🔄 Creating release..."

# Update .VERSION file
echo "📝 Updating .VERSION file..."
VERSION_NUM=${VERSION#v}  # Remove 'v' prefix for .VERSION file
echo "$VERSION_NUM" > src/.VERSION
git add src/.VERSION
git commit -m "Bump version to $VERSION"
echo "✅ .VERSION file updated and committed"

# Create the tag with annotation
git tag -a "$VERSION" -m "$TYPE_EMOJI $RELEASE_TITLE

$FULL_DESCRIPTION"

echo "✅ Created tag: $VERSION"

# Push the tag to origin
echo "📤 Pushing tag to origin..."
git push origin "$VERSION"
echo "✅ Tag pushed to origin"

# Push current branch if it has unpushed commits
UNPUSHED=$(git log origin/$CURRENT_BRANCH..$CURRENT_BRANCH --oneline 2>/dev/null || echo "")
if [[ -n $UNPUSHED ]]; then
    echo "📤 Pushing current branch..."
    git push origin "$CURRENT_BRANCH"
    echo "✅ Branch pushed to origin"
fi

# Create GitHub release if gh CLI is available
if [[ "$GH_AVAILABLE" = true ]]; then
    echo ""
    read -p "🐙 Create GitHub release? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "📤 Creating GitHub release..."
        
        # Determine if it's a prerelease
        PRERELEASE_FLAG=""
        if [[ $VERSION =~ (alpha|beta|rc) ]]; then
            PRERELEASE_FLAG="--prerelease"
        fi
        
        gh release create "$VERSION" \
        --title "$TYPE_EMOJI $RELEASE_TITLE" \
        --notes "$FULL_DESCRIPTION" \
        $PRERELEASE_FLAG
        
        echo "✅ GitHub release created"
    fi
fi

echo ""
echo "🎉 Release $VERSION created successfully!"
echo ""
echo "📌 What was done:"
echo "  • Created annotated tag: $VERSION"
echo "  • Pushed tag to origin"
echo "  • Pushed branch: $CURRENT_BRANCH"
if [[ "$GH_AVAILABLE" = true ]]; then
    echo "  • Created GitHub release (if requested)"
fi
echo ""
echo "🔗 Useful commands:"
echo "  • View tag: git show $VERSION"
echo "  • List all tags: git tag -l"
echo "  • Delete tag (if needed): git tag -d $VERSION && git push origin :refs/tags/$VERSION"
if [[ "$GH_AVAILABLE" = true ]]; then
    echo "  • View releases: gh release list"
fi