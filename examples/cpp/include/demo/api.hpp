#pragma once

#include <cstddef>
#include <initializer_list>
#include <string>
#include <type_traits>

/// @brief Demonstration API used by the mkdocstrings-cpp documentation site.
///
/// This namespace exercises common C++ declaration shapes that a real
/// library would expose: class templates, enum classes, function
/// templates, overload sets, type traits, and C++20 concepts.
namespace demo {

// ---------------------------------------------------------------------------
// Forward declarations
// ---------------------------------------------------------------------------

template <typename T, std::size_t N>
class Vector;

// ---------------------------------------------------------------------------
// Enum
// ---------------------------------------------------------------------------

/// @brief Output channel used when formatting results.
///
/// @details Each channel selects a different serialization backend.
enum class Channel {
    /// Human-readable text written to the terminal.
    Console,
    /// Structured JSON output suitable for log ingestion.
    Json,
    /// Compact binary archive (MessagePack-compatible).
    Binary,
};

// ---------------------------------------------------------------------------
// Alias
// ---------------------------------------------------------------------------

/// @brief Convenience alias for object labels shown in diagnostics and
/// examples.
using Label = std::string;

// ---------------------------------------------------------------------------
// Concept (C++20)
// ---------------------------------------------------------------------------

/// @brief Concept satisfied by types whose values are comparable with
/// `operator==`.
///
/// @details Used to constrain equality-based helper functions such as
/// `demo::contains`.  Any type that provides a non-throwing `==`
/// operator models this concept.
///
/// @tparam T Candidate type.
template <typename T>
concept EqualityComparable = requires(const T& a, const T& b) {
    { a == b } -> std::convertible_to<bool>;
};

// ---------------------------------------------------------------------------
// Type trait
// ---------------------------------------------------------------------------

/// @brief Type trait that detects whether a type is a `demo::Vector`
/// specialization.
///
/// @tparam T Candidate type.
template <typename T>
struct is_vector : std::false_type {};

/// @brief Specialization of `is_vector` for `demo::Vector`.
///
/// @tparam T Scalar value type.
/// @tparam N Number of elements.
template <typename T, std::size_t N>
struct is_vector<Vector<T, N>> : std::true_type {};

// ---------------------------------------------------------------------------
// Class template
// ---------------------------------------------------------------------------

/// @brief A fixed-size mathematical vector stored on the stack.
///
/// `Vector` is intentionally small, but it exercises the Doxygen XML
/// shapes needed by real C++ APIs: class templates, constructors,
/// operators, member functions, and member templates.
///
/// @tparam T Scalar value type stored in each element.
/// @tparam N Number of elements in the vector.
template <typename T, std::size_t N>
class Vector {
public:
    /// @brief Value type stored in the vector.
    using value_type = T;

    /// @brief Number of elements in this vector type.
    static constexpr std::size_t extent = N;

    /// @brief Construct an empty vector with value-initialized elements.
    Vector() = default;

    /// @brief Construct from an initializer list.
    ///
    /// Extra values are ignored and missing values are value-initialized.
    ///
    /// @param values Input values copied into the vector.
    Vector(std::initializer_list<T> values);

    /// @brief Return the number of elements.
    ///
    /// @return The compile-time extent `N`.
    [[nodiscard]] constexpr std::size_t size() const noexcept { return N; }

    /// @brief Read an element by index.
    ///
    /// @param index Zero-based element index.
    /// @return A const reference to the selected element.
    [[nodiscard]] constexpr const T& operator[](std::size_t index) const noexcept;

    /// @brief Write an element by index.
    ///
    /// @param index Zero-based element index.
    /// @return A mutable reference to the selected element.
    [[nodiscard]] constexpr T& operator[](std::size_t index) noexcept;

    /// @brief Convert the vector to another scalar type.
    ///
    /// @tparam U Destination scalar type.
    /// @return A vector with each element converted to `U`.
    template <typename U>
    [[nodiscard]] Vector<U, N> cast() const;

private:
    T data_[N]{};
};

// ---------------------------------------------------------------------------
// Struct
// ---------------------------------------------------------------------------

/// @brief Runtime metadata attached to a value.
struct Metadata {
    /// @brief API-facing label shown in diagnostics.
    Label label;
    /// @brief Output channel used by serializers.
    Channel channel = Channel::Console;
};

// ---------------------------------------------------------------------------
// Free function templates
// ---------------------------------------------------------------------------

/// @brief Compute the dot product between two vectors.
///
/// @tparam T Scalar value type.
/// @tparam N Number of elements.
/// @param lhs Left vector.
/// @param rhs Right vector.
/// @return Dot product of `lhs` and `rhs`.
template <typename T, std::size_t N>
[[nodiscard]] T dot(const Vector<T, N>& lhs, const Vector<T, N>& rhs);

/// @brief Clamp a value into a closed interval.
///
/// @tparam T Ordered scalar type.
/// @param value Input value.
/// @param lower Lower bound.
/// @param upper Upper bound.
/// @return `value` clipped to `[lower, upper]`.
template <typename T>
[[nodiscard]] constexpr T clamp(T value, T lower, T upper);

/// @brief Test whether a range contains a value.
///
/// @tparam T Type that satisfies `demo::EqualityComparable`.
/// @param haystack Range to search.
/// @param needle Value to find.
/// @return `true` when `needle` is present in `haystack`.
template <EqualityComparable T, std::size_t N>
[[nodiscard]] constexpr bool contains(const Vector<T, N>& haystack, const T& needle);

// ---------------------------------------------------------------------------
// Overloaded function templates
// ---------------------------------------------------------------------------

/// @brief Format a vector with the default label.
///
/// @param vector Vector to format.
/// @return A human-readable string.
template <typename T, std::size_t N>
[[nodiscard]] std::string format(const Vector<T, N>& vector);

/// @brief Format a vector with metadata.
///
/// @param vector Vector to format.
/// @param metadata Runtime metadata controlling the output shape.
/// @return A formatted string.
template <typename T, std::size_t N>
[[nodiscard]] std::string format(const Vector<T, N>& vector, const Metadata& metadata);

} // namespace demo
